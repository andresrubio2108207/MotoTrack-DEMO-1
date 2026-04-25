"""Tests para el servicio de alertas."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.user import User
from app.models.motorcycle import Motorcycle
from app.services.auth_service import hash_password
from app.services.maintenance_service import create_maintenance
from app.services.alert_service import (
    create_alert,
    get_active_alerts,
    get_all_alerts,
    resolve_alert,
    generate_alerts_for_motorcycle,
    generate_alerts_all_motorcycles,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def db():
    """Base de datos SQLite en memoria."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    from app.models import maintenance, alert  # noqa: F401
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def motorcycle(db):
    """Crea un usuario y motocicleta de prueba."""
    user = User(username="alert_user", email="alert@test.com", hashed_password=hash_password("pass"))
    db.add(user)
    db.flush()

    moto = Motorcycle(user_id=user.id, brand="Honda", model="CB500F", year=2021, current_km=10000.0)
    db.add(moto)
    db.commit()
    db.refresh(moto)
    return moto


# ─── Tests de creación de alertas ─────────────────────────────────────────────

class TestCreateAlert:
    def test_create_alert_with_date(self, db, motorcycle):
        """create_alert debe crear una alerta con due_date correctamente."""
        due = datetime.utcnow() + timedelta(days=5)
        alert = create_alert(db, motorcycle.id, "Mantenimiento próximo", due_date=due)
        assert alert.id is not None
        assert alert.motorcycle_id == motorcycle.id
        assert alert.resolved is False
        assert alert.due_date == due

    def test_create_alert_with_km(self, db, motorcycle):
        """create_alert debe crear una alerta con due_km correctamente."""
        alert = create_alert(db, motorcycle.id, "Cambio de aceite pronto", due_km=11000.0)
        assert alert.id is not None
        assert alert.due_km == 11000.0
        assert alert.resolved is False

    def test_create_alert_defaults_not_resolved(self, db, motorcycle):
        """Una alerta recién creada debe estar no resuelta."""
        alert = create_alert(db, motorcycle.id, "Test alert")
        assert alert.resolved is False

    def test_create_alert_without_due(self, db, motorcycle):
        """Se puede crear una alerta sin due_date ni due_km."""
        alert = create_alert(db, motorcycle.id, "Alerta genérica")
        assert alert.due_date is None
        assert alert.due_km is None


# ─── Tests de obtener alertas activas ─────────────────────────────────────────

class TestGetActiveAlerts:
    def test_get_active_returns_only_unresolved(self, db, motorcycle):
        """get_active_alerts debe retornar solo alertas no resueltas."""
        create_alert(db, motorcycle.id, "Activa 1")
        create_alert(db, motorcycle.id, "Activa 2")
        a3 = create_alert(db, motorcycle.id, "Resuelta")
        resolve_alert(db, a3.id)

        active = get_active_alerts(db, motorcycle.id)
        assert len(active) == 2
        assert all(not a.resolved for a in active)

    def test_get_active_empty_when_all_resolved(self, db, motorcycle):
        """get_active_alerts debe retornar lista vacía si todo está resuelto."""
        a = create_alert(db, motorcycle.id, "La única")
        resolve_alert(db, a.id)
        active = get_active_alerts(db, motorcycle.id)
        assert active == []

    def test_get_active_empty_for_new_motorcycle(self, db, motorcycle):
        """get_active_alerts debe retornar lista vacía para moto sin alertas."""
        active = get_active_alerts(db, motorcycle.id)
        assert active == []


# ─── Tests de obtener todas las alertas ───────────────────────────────────────

class TestGetAllAlerts:
    def test_get_all_includes_resolved(self, db, motorcycle):
        """get_all_alerts debe incluir alertas resueltas."""
        create_alert(db, motorcycle.id, "Activa")
        a2 = create_alert(db, motorcycle.id, "Resuelta")
        resolve_alert(db, a2.id)

        all_alerts = get_all_alerts(db, motorcycle.id)
        assert len(all_alerts) == 2

    def test_get_all_isolated_by_motorcycle(self, db, motorcycle):
        """get_all_alerts no debe incluir alertas de otra motocicleta."""
        # Crear segunda moto en la misma fixture
        user = db.query(User).filter(User.username == "alert_user").first()
        moto2 = Motorcycle(user_id=user.id, brand="Yamaha", model="R3", current_km=0.0)
        db.add(moto2)
        db.commit()
        db.refresh(moto2)

        create_alert(db, moto2.id, "Alerta de otra moto")
        all_alerts = get_all_alerts(db, motorcycle.id)
        assert all_alerts == []


# ─── Tests de resolver alerta ─────────────────────────────────────────────────

class TestResolveAlert:
    def test_resolve_alert_success(self, db, motorcycle):
        """resolve_alert debe marcar la alerta como resuelta."""
        alert = create_alert(db, motorcycle.id, "Por resolver")
        result = resolve_alert(db, alert.id)
        assert result is not None
        assert result.resolved is True

    def test_resolve_nonexistent_returns_none(self, db):
        """resolve_alert con ID inexistente debe retornar None."""
        result = resolve_alert(db, 99999)
        assert result is None

    def test_already_resolved_can_resolve_again(self, db, motorcycle):
        """resolve_alert sobre una alerta ya resuelta debe funcionar sin error."""
        alert = create_alert(db, motorcycle.id, "Test")
        resolve_alert(db, alert.id)
        result = resolve_alert(db, alert.id)
        assert result.resolved is True


# ─── Tests de generación automática de alertas ────────────────────────────────

class TestGenerateAlertsForMotorcycle:
    def test_generates_alert_for_overdue_date(self, db, motorcycle):
        """Debe generar alerta cuando la fecha del próximo mantenimiento ya venció."""
        from app.models.maintenance import Maintenance

        past_date = datetime.utcnow() - timedelta(days=10)
        m = Maintenance(
            motorcycle_id=motorcycle.id,
            type="Cambio de aceite",
            date=datetime.utcnow() - timedelta(days=100),
            km=9000.0,
            completed=True,
            next_km=15000.0,
            next_date=past_date,  # Fecha vencida
        )
        db.add(m)
        db.commit()

        alerts = generate_alerts_for_motorcycle(db, motorcycle.id)
        assert len(alerts) >= 1

    def test_generates_alert_for_near_km(self, db, motorcycle):
        """Debe generar alerta cuando los km actuales están cerca del próximo mantenimiento."""
        from app.models.maintenance import Maintenance

        # Moto con 10000 km, próximo mantenimiento a 10300 km (dentro del umbral de 500)
        motorcycle.current_km = 10000.0
        m = Maintenance(
            motorcycle_id=motorcycle.id,
            type="Revisión de cadena",
            date=datetime.utcnow() - timedelta(days=30),
            km=8500.0,
            completed=True,
            next_km=10300.0,  # Solo 300 km de margen → alerta
            next_date=datetime.utcnow() + timedelta(days=365),
        )
        db.add(m)
        db.commit()

        alerts = generate_alerts_for_motorcycle(db, motorcycle.id)
        assert len(alerts) >= 1

    def test_no_alerts_for_future_maintenance(self, db, motorcycle):
        """No debe generar alertas si el próximo mantenimiento está lejos."""
        from app.models.maintenance import Maintenance

        m = Maintenance(
            motorcycle_id=motorcycle.id,
            type="Cambio de aceite",
            date=datetime.utcnow(),
            km=10000.0,
            completed=True,
            next_km=15000.0,  # 5000 km lejos → sin alerta
            next_date=datetime.utcnow() + timedelta(days=60),  # 60 días lejos
        )
        db.add(m)
        db.commit()

        motorcycle.current_km = 10000.0
        db.commit()

        alerts = generate_alerts_for_motorcycle(db, motorcycle.id)
        assert alerts == []

    def test_no_duplicate_alerts(self, db, motorcycle):
        """No debe crear alertas duplicadas si ya existe una activa para el mismo tipo."""
        from app.models.maintenance import Maintenance

        past_date = datetime.utcnow() - timedelta(days=5)
        m = Maintenance(
            motorcycle_id=motorcycle.id,
            type="Cambio de aceite",
            date=datetime.utcnow() - timedelta(days=100),
            km=9000.0,
            completed=True,
            next_km=15000.0,
            next_date=past_date,
        )
        db.add(m)
        db.commit()

        # Primera generación
        alerts1 = generate_alerts_for_motorcycle(db, motorcycle.id)
        # Segunda generación (no debe duplicar)
        alerts2 = generate_alerts_for_motorcycle(db, motorcycle.id)
        assert len(alerts2) == 0


# ─── Tests de generación global de alertas ────────────────────────────────────

class TestGenerateAlertsAllMotorcycles:
    def test_generates_for_all_motorcycles(self, db):
        """generate_alerts_all_motorcycles debe procesar todas las motos."""
        from app.models.maintenance import Maintenance

        user = User(username="global_user", email="global@test.com", hashed_password=hash_password("pass"))
        db.add(user)
        db.flush()

        moto1 = Motorcycle(user_id=user.id, brand="Honda", model="A", current_km=10000.0)
        moto2 = Motorcycle(user_id=user.id, brand="Yamaha", model="B", current_km=5000.0)
        db.add_all([moto1, moto2])
        db.commit()
        db.refresh(moto1)
        db.refresh(moto2)

        # Mantenimiento vencido en moto1
        past = datetime.utcnow() - timedelta(days=5)
        m1 = Maintenance(
            motorcycle_id=moto1.id,
            type="Cambio de aceite",
            date=datetime.utcnow() - timedelta(days=100),
            km=9000.0,
            completed=True,
            next_km=15000.0,
            next_date=past,
        )
        db.add(m1)
        db.commit()

        count = generate_alerts_all_motorcycles(db)
        assert count >= 1
