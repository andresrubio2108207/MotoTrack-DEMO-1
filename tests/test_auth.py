import os
import tempfile

from app.database.engine import configure_database, dispose_engine, init_db
from app.services.auth_service import (
    add_motorcycle,
    authenticate_user,
    delete_motorcycle,
    get_user_by_email,
    list_user_motorcycles,
    register_user,
    update_motorcycle,
)

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


def test_register_and_authenticate_user():
    user = register_user("Andrea", "andrea@example.com", "secret123")

    assert user.id is not None
    assert user.password != "secret123"
    assert get_user_by_email("andrea@example.com").email == "andrea@example.com"
    assert authenticate_user("andrea@example.com", "secret123") is not None
    assert authenticate_user("andrea@example.com", "wrong-pass") is None


def test_add_motorcycle_to_user():
    user = register_user("Andrea", "andrea@example.com", "secret123")
    motorcycle = add_motorcycle(user.id, "Honda", "CB125F", 2025, "abc123", 980.5)

    motorcycles = list_user_motorcycles(user.id)

    assert motorcycle.plate == "ABC123"
    assert len(motorcycles) == 1
    assert motorcycles[0].brand == "Honda"


def test_update_and_delete_motorcycle():
    user = register_user("Andrea", "andrea@example.com", "secret123")
    motorcycle = add_motorcycle(user.id, "Honda", "CB125F", 2025, "abc123", 980.5)

    updated = update_motorcycle(motorcycle.id, brand="Yamaha", plate="xyz987", current_km=1200)

    assert updated.brand == "Yamaha"
    assert updated.plate == "XYZ987"
    assert delete_motorcycle(motorcycle.id) is True
    assert list_user_motorcycles(user.id) == []
