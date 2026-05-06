from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.database.engine import init_db, session_scope
from app.models import Alert, Maintenance, Motorcycle, User


def seed_database(force_reset: bool = False) -> None:
    init_db(drop_existing=force_reset)

    with session_scope() as session:
        existing_user = session.query(User).filter_by(email="demo@mototrack.local").first()
        if existing_user is not None:
            return

        user = User(
            name="Demo Rider",
            email="demo@mototrack.local",
            password="demo1234",
        )
        session.add(user)
        session.flush()

        motorcycle = Motorcycle(
            user_id=user.id,
            brand="Yamaha",
            model="FZ 2.0",
            year=2024,
            plate="DEM001",
            current_km=15250,
        )
        session.add(motorcycle)
        session.flush()

        session.add(
            Maintenance(
                motorcycle_id=motorcycle.id,
                type="Cambio de aceite",
                description="Servicio preventivo inicial",
                km_at_service=15000,
                cost=120000,
                service_date=datetime.now(timezone.utc) - timedelta(days=10),
                next_service_km=18000,
            )
        )

        session.add_all(
            [
                Alert(
                    motorcycle_id=motorcycle.id,
                    title="Próximo cambio de aceite",
                    trigger_type="km",
                    trigger_km=18000,
                ),
                Alert(
                    motorcycle_id=motorcycle.id,
                    title="Revisión técnico-mecánica",
                    trigger_type="date",
                    trigger_date=datetime.now(timezone.utc) + timedelta(days=30),
                ),
            ]
        )
