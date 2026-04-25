"""Tests para el servicio de mantenimientos."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.user import User
from app.models.motorcycle import Motorcycle
from app.services.auth_service import hash_password
from app.services.maintenance_service import (
    create_maintenance,
    get_maintenance_history,
    complete_maintenance,
    calculate_next_maintenance,
    get_pending_maintenances,
    MAINTENANCE_INTERVALS,
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
def user_and_moto(db):
    """Crea un usuario y motocicleta de prueba."""
    user = User(username="maint_user", email="maint@test.com", hashed_password=hash_password("pass"))
    db.add(user)
    db.flush()

    moto = Motorcycle(user_id=user.id, brand="Honda", model="CB500F", year=2021, current_km=10000.0)
    db.add(moto)
    db.commit()
    db.refresh(moto)
    return user, moto


# ─── Tests de creación de mantenimiento ───────────────────────────────────────

class TestCreateMaintenance:
    def test_create_basic_maintenance(self, db, user_and_moto):
        """create_maintenance debe retornar un objeto Maintenance válido."""
        _, moto = user_and_moto
        m = create_maintenance(db, moto.id, "Cambio de aceite", km=10000.0, description="Aceite sintético")
        assert m.id is not None
        assert m.type == "Cambio de aceite"
        assert m.km == 10000.0
        assert m.completed is True
        assert m.next_km is not None

    def test_create_maintenance_calculates_next_km(self, db, user_and_moto):
        """El próximo km debe calcularse según el intervalo del tipo."""
        _, moto = user_and_moto
        interval = MAINTENANCE_INTERVALS["Cambio de aceite"]["km"]
        m = create_maintenance(db, moto.id, "Cambio de aceite", km=5000.0)
        assert m.next_km == 5000.0 + interval

    def test_create_maintenance_calculates_next_date(self, db, user_and_moto):
        """La próxima fecha debe calcularse según el intervalo del tipo."""
        _, moto = user_and_moto
        interval_days = MAINTENANCE_INTERVALS["Cambio de aceite"]["days"]
        now = datetime.utcnow()
        m = create_maintenance(db, moto.id, "Cambio de aceite", km=5000.0, date=now)
        expected_date = now + timedelta(days=interval_days)
        # Tolerancia de 1 segundo
        diff = abs((m.next_date - expected_date).total_seconds())
        assert diff < 1

    def test_create_maintenance_updates_moto_km(self, db, user_and_moto):
        """Si los km del mantenimiento > km actuales, se actualiza la moto."""
        _, moto = user_and_moto
        original_km = moto.current_km
        new_km = original_km + 1000
        create_maintenance(db, moto.id, "Cambio de aceite", km=new_km)
        db.refresh(moto)
        assert moto.current_km == new_km

    def test_create_maintenance_does_not_reduce_moto_km(self, db, user_and_moto):
        """Los km de la moto no deben reducirse si el mantenimiento tiene km menores."""
        _, moto = user_and_moto
        original_km = moto.current_km
        create_maintenance(db, moto.id, "Cambio de aceite", km=original_km - 500)
        db.refresh(moto)
        assert moto.current_km == original_km

    def test_create_maintenance_with_custom_date(self, db, user_and_moto):
        """Se debe respetar la fecha personalizada al crear el mantenimiento."""
        _, moto = user_and_moto
        custom_date = datetime(2023, 6, 15)
        m = create_maintenance(db, moto.id, "Revisión de frenos", km=8000.0, date=custom_date)
        assert m.date == custom_date

    def test_create_maintenance_unknown_type(self, db, user_and_moto):
        """Tipo desconocido debe usar intervalo por defecto."""
        _, moto = user_and_moto
        m = create_maintenance(db, moto.id, "Tipo desconocido", km=5000.0)
        assert m.next_km == 5000.0 + 5000  # Valor por defecto


# ─── Tests de historial ───────────────────────────────────────────────────────

class TestGetMaintenanceHistory:
    def test_history_returns_all_records(self, db, user_and_moto):
        """El historial debe retornar todos los mantenimientos de la moto."""
        _, moto = user_and_moto
        create_maintenance(db, moto.id, "Cambio de aceite", km=5000.0)
        create_maintenance(db, moto.id, "Revisión de frenos", km=6000.0)
        history = get_maintenance_history(db, moto.id)
        assert len(history) == 2

    def test_history_empty_for_new_moto(self, db, user_and_moto):
        """El historial debe estar vacío para una moto nueva."""
        _, moto = user_and_moto
        history = get_maintenance_history(db, moto.id)
        assert history == []

    def test_history_ordered_by_date_desc(self, db, user_and_moto):
        """El historial debe estar ordenado por fecha descendente."""
        _, moto = user_and_moto
        date1 = datetime(2023, 1, 1)
        date2 = datetime(2023, 6, 1)
        create_maintenance(db, moto.id, "Cambio de aceite", km=5000.0, date=date1)
        create_maintenance(db, moto.id, "Revisión de frenos", km=6000.0, date=date2)
        history = get_maintenance_history(db, moto.id)
        assert history[0].date > history[1].date

    def test_history_isolated_by_motorcycle(self, db, user_and_moto):
        """El historial de una moto no debe incluir registros de otra."""
        user, moto1 = user_and_moto
        moto2 = Motorcycle(user_id=user.id, brand="Yamaha", model="MT07", current_km=0.0)
        db.add(moto2)
        db.commit()
        db.refresh(moto2)

        create_maintenance(db, moto1.id, "Cambio de aceite", km=5000.0)
        assert get_maintenance_history(db, moto2.id) == []


# ─── Tests de completar mantenimiento ─────────────────────────────────────────

class TestCompleteMaintenance:
    def test_complete_maintenance_success(self, db, user_and_moto):
        """complete_maintenance debe marcar el mantenimiento como completado."""
        _, moto = user_and_moto
        m = create_maintenance(db, moto.id, "Cambio de aceite", km=5000.0)
        # Simular pendiente
        m.completed = False
        db.commit()

        result = complete_maintenance(db, m.id)
        assert result is not None
        assert result.completed is True

    def test_complete_nonexistent_returns_none(self, db):
        """complete_maintenance con ID inexistente debe retornar None."""
        result = complete_maintenance(db, 9999)
        assert result is None


# ─── Tests de cálculo de próximo mantenimiento ────────────────────────────────

class TestCalculateNextMaintenance:
    def test_calculate_next_maintenance_known_type(self):
        """Debe calcular correctamente para tipos conocidos."""
        date = datetime(2023, 1, 1)
        result = calculate_next_maintenance("Cambio de aceite", 5000.0, date)
        interval = MAINTENANCE_INTERVALS["Cambio de aceite"]
        assert result["next_km"] == 5000.0 + interval["km"]
        assert result["next_date"] == date + timedelta(days=interval["days"])

    def test_calculate_next_maintenance_unknown_type(self):
        """Tipo desconocido debe usar valores por defecto."""
        date = datetime(2023, 1, 1)
        result = calculate_next_maintenance("Tipo raro", 1000.0, date)
        assert result["next_km"] == 1000.0 + 5000
        assert result["next_date"] == date + timedelta(days=180)


# ─── Tests de mantenimientos pendientes ───────────────────────────────────────

class TestGetPendingMaintenances:
    def test_get_pending_returns_incomplete(self, db, user_and_moto):
        """get_pending_maintenances debe retornar solo mantenimientos incompletos."""
        _, moto = user_and_moto
        m = create_maintenance(db, moto.id, "Cambio de aceite", km=5000.0)
        m.completed = False
        db.commit()

        pending = get_pending_maintenances(db, moto.id)
        assert len(pending) == 1
        assert pending[0].completed is False

    def test_get_pending_excludes_completed(self, db, user_and_moto):
        """get_pending_maintenances no debe retornar mantenimientos completados."""
        _, moto = user_and_moto
        create_maintenance(db, moto.id, "Cambio de aceite", km=5000.0)  # completed=True
        pending = get_pending_maintenances(db, moto.id)
        assert pending == []
