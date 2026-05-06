import os
import tempfile
from datetime import datetime, timezone

from app.database.engine import configure_database, dispose_engine, init_db
from app.services.auth_service import add_motorcycle, register_user
from app.services.maintenance_service import create_maintenance, list_maintenances

TEST_DB_PATH = None


def setup_function():
    global TEST_DB_PATH
    fd, TEST_DB_PATH = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    configure_database(f"sqlite:///{TEST_DB_PATH}")
    init_db(drop_existing=True)


def teardown_function():
    global TEST_DB_PATH
    dispose_engine()
    if TEST_DB_PATH and os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    TEST_DB_PATH = None


def test_create_maintenance_updates_motorcycle_km():
    user = register_user("Andrea", "andrea@example.com", "secret123")
    motorcycle = add_motorcycle(user.id, "Suzuki", "GN125", 2023, "suz321", 9000)

    maintenance = create_maintenance(
        motorcycle_id=motorcycle.id,
        type="Cambio de aceite",
        km_at_service=9500,
        service_date=datetime.now(timezone.utc),
        cost=85000,
        next_service_km=12000,
    )

    history = list_maintenances(motorcycle.id)

    assert maintenance.id is not None
    assert len(history) == 1
    assert history[0].km_at_service == 9500
