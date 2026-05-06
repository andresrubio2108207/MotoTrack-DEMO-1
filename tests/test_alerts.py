import os
import tempfile
from datetime import datetime, timedelta, timezone

from app.database.engine import configure_database, dispose_engine, init_db
from app.services.alert_service import create_alert, evaluate_alerts, list_alerts
from app.services.auth_service import add_motorcycle, register_user, update_motorcycle

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


def test_km_alert_fires_when_motorcycle_reaches_threshold():
    user = register_user("Andrea", "andrea@example.com", "secret123")
    motorcycle = add_motorcycle(user.id, "Bajaj", "Boxer", 2022, "box111", 4900)
    alert = create_alert(motorcycle.id, "Cambio de aceite", "km", trigger_km=5000)

    update_motorcycle(motorcycle.id, current_km=5100)
    fired_alerts = evaluate_alerts()

    assert alert.id is not None
    assert len(fired_alerts) == 1
    assert fired_alerts[0].is_fired is True


def test_date_alert_fires_when_due_date_passes():
    user = register_user("Andrea", "andrea@example.com", "secret123")
    motorcycle = add_motorcycle(user.id, "AKT", "NKD", 2021, "akt222", 12000)

    create_alert(
        motorcycle.id,
        "SOAT",
        "date",
        trigger_date=datetime.now(timezone.utc) - timedelta(days=1),
    )

    fired_alerts = evaluate_alerts()
    alerts = list_alerts(motorcycle.id)

    assert len(fired_alerts) == 1
    assert alerts[0].is_fired is True
