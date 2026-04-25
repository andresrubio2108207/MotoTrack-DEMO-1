"""Datos de ejemplo (seed) para la demo de MotoTrack PRO."""

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database.engine import SessionLocal
from app.models.user import User
from app.models.motorcycle import Motorcycle
from app.models.maintenance import Maintenance
from app.models.alert import Alert
from app.services.auth_service import hash_password

logger = logging.getLogger(__name__)


def seed_database():
    """Inserta datos de ejemplo si la base de datos está vacía."""
    db: Session = SessionLocal()
    try:
        # Verificar si ya hay datos
        if db.query(User).count() > 0:
            logger.info("La base de datos ya tiene datos. Seed omitido.")
            return

        logger.info("Insertando datos de ejemplo...")

        # --- Usuarios demo ---
        user1 = User(
            username="demo",
            email="demo@mototrack.com",
            hashed_password=hash_password("demo1234"),
        )
        user2 = User(
            username="carlos",
            email="carlos@mototrack.com",
            hashed_password=hash_password("carlos123"),
        )
        db.add_all([user1, user2])
        db.flush()

        # --- Motocicletas demo ---
        moto1 = Motorcycle(
            user_id=user1.id,
            brand="Honda",
            model="CB 500F",
            year=2021,
            current_km=12500.0,
        )
        moto2 = Motorcycle(
            user_id=user1.id,
            brand="Yamaha",
            model="MT-07",
            year=2022,
            current_km=8300.0,
        )
        moto3 = Motorcycle(
            user_id=user2.id,
            brand="Kawasaki",
            model="Z400",
            year=2023,
            current_km=3200.0,
        )
        db.add_all([moto1, moto2, moto3])
        db.flush()

        now = datetime.utcnow()

        # --- Mantenimientos demo para moto1 ---
        maintenances = [
            Maintenance(
                motorcycle_id=moto1.id,
                type="Cambio de aceite",
                date=now - timedelta(days=95),
                km=9500.0,
                description="Aceite 10W-40 sintético. Filtro de aceite incluido.",
                completed=True,
                next_km=12500.0,
                next_date=now - timedelta(days=5),  # Ya venció → generará alerta
            ),
            Maintenance(
                motorcycle_id=moto1.id,
                type="Revisión de frenos",
                date=now - timedelta(days=60),
                km=11000.0,
                description="Pastillas delanteras al 40%. Líquido de frenos OK.",
                completed=True,
                next_km=16000.0,
                next_date=now + timedelta(days=120),
            ),
            Maintenance(
                motorcycle_id=moto1.id,
                type="Revisión de cadena",
                date=now - timedelta(days=30),
                km=12000.0,
                description="Cadena lubricada y ajustada.",
                completed=True,
                next_km=13500.0,
                next_date=now + timedelta(days=0),  # Hoy → alerta por fecha
            ),
        ]

        # --- Mantenimiento demo para moto2 ---
        maintenances += [
            Maintenance(
                motorcycle_id=moto2.id,
                type="Cambio de aceite",
                date=now - timedelta(days=45),
                km=7800.0,
                description="Aceite 10W-40 semisintético.",
                completed=True,
                next_km=10800.0,
                next_date=now + timedelta(days=45),
            ),
            Maintenance(
                motorcycle_id=moto2.id,
                type="Cambio de filtro de aire",
                date=now - timedelta(days=200),
                km=5000.0,
                description="Filtro de papel reemplazado.",
                completed=True,
                next_km=13000.0,
                next_date=now + timedelta(days=165),
            ),
        ]

        db.add_all(maintenances)
        db.flush()

        # --- Alertas demo ---
        alerts = [
            Alert(
                motorcycle_id=moto1.id,
                message="⏰ Próximo Cambio de aceite vencido. Realiza el mantenimiento.",
                due_date=now - timedelta(days=5),
                resolved=False,
            ),
            Alert(
                motorcycle_id=moto1.id,
                message="🔧 Revisión de cadena requerida hoy. Km actual: 12500",
                due_km=13500.0,
                resolved=False,
            ),
            Alert(
                motorcycle_id=moto2.id,
                message="✅ Cambio de aceite completado exitosamente.",
                resolved=True,
            ),
        ]
        db.add_all(alerts)

        db.commit()
        logger.info("✅ Datos de ejemplo insertados correctamente.")
        logger.info(f"   Usuarios: demo / demo1234, carlos / carlos123")

    except Exception as e:
        db.rollback()
        logger.error(f"Error al insertar datos de ejemplo: {e}")
        raise
    finally:
        db.close()
