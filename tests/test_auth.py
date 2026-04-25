"""Tests para el servicio de autenticación."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.user import User
from app.services.auth_service import (
    hash_password,
    verify_password,
    register_user,
    login_user,
    create_access_token,
    decode_token,
    get_user_by_id,
)


# ─── Fixture de base de datos en memoria ──────────────────────────────────────

@pytest.fixture(scope="function")
def db():
    """Crea una base de datos SQLite en memoria para cada test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    # Importar todos los modelos para que se registren
    from app.models import motorcycle, maintenance, alert  # noqa: F401
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


# ─── Tests de hash de contraseña ──────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_password_returns_non_plain(self):
        """El hash no debe ser igual a la contraseña original."""
        password = "secret123"
        hashed = hash_password(password)
        assert hashed != password

    def test_verify_password_correct(self):
        """verify_password debe retornar True para contraseña correcta."""
        password = "mypassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """verify_password debe retornar False para contraseña incorrecta."""
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_hash_is_unique(self):
        """Dos hashes del mismo password deben ser distintos (salts únicos)."""
        pw = "samepassword"
        h1 = hash_password(pw)
        h2 = hash_password(pw)
        assert h1 != h2


# ─── Tests de JWT ─────────────────────────────────────────────────────────────

class TestJWT:
    def test_create_and_decode_token(self):
        """El token generado debe poder decodificarse correctamente."""
        data = {"sub": "testuser", "user_id": 1}
        token = create_access_token(data)
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "testuser"
        assert decoded["user_id"] == 1

    def test_decode_invalid_token_returns_none(self):
        """Un token inválido debe retornar None."""
        result = decode_token("not.a.valid.token")
        assert result is None

    def test_decode_tampered_token_returns_none(self):
        """Un token alterado debe retornar None."""
        token = create_access_token({"sub": "user"})
        tampered = token[:-5] + "XXXXX"
        result = decode_token(tampered)
        assert result is None


# ─── Tests de registro de usuario ─────────────────────────────────────────────

class TestRegisterUser:
    def test_register_user_success(self, db):
        """Registro exitoso debe retornar un usuario con los datos correctos."""
        user = register_user(db, "testuser", "test@example.com", "password123")
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password != "password123"

    def test_register_duplicate_username_raises(self, db):
        """Registrar un username duplicado debe lanzar ValueError."""
        register_user(db, "duplicate", "first@example.com", "pass1")
        with pytest.raises(ValueError, match="ya está en uso"):
            register_user(db, "duplicate", "second@example.com", "pass2")

    def test_register_duplicate_email_raises(self, db):
        """Registrar un email duplicado debe lanzar ValueError."""
        register_user(db, "user1", "same@example.com", "pass1")
        with pytest.raises(ValueError, match="ya está registrado"):
            register_user(db, "user2", "same@example.com", "pass2")

    def test_register_persists_in_db(self, db):
        """El usuario registrado debe persistir en la base de datos."""
        register_user(db, "persistent", "persistent@example.com", "pass")
        stored = db.query(User).filter(User.username == "persistent").first()
        assert stored is not None
        assert stored.email == "persistent@example.com"


# ─── Tests de login de usuario ────────────────────────────────────────────────

class TestLoginUser:
    def test_login_success(self, db):
        """Login exitoso debe retornar user y access_token."""
        register_user(db, "loginuser", "login@example.com", "mypass")
        result = login_user(db, "loginuser", "mypass")
        assert result["user"].username == "loginuser"
        assert result["access_token"] is not None
        assert result["token_type"] == "bearer"

    def test_login_wrong_password(self, db):
        """Login con contraseña incorrecta debe lanzar ValueError."""
        register_user(db, "user_wp", "wp@example.com", "correct")
        with pytest.raises(ValueError, match="Credenciales incorrectas"):
            login_user(db, "user_wp", "wrong")

    def test_login_nonexistent_user(self, db):
        """Login con usuario inexistente debe lanzar ValueError."""
        with pytest.raises(ValueError, match="Credenciales incorrectas"):
            login_user(db, "nobody", "pass")

    def test_login_token_contains_user_info(self, db):
        """El token JWT del login debe contener el username y user_id."""
        register_user(db, "tokenuser", "token@example.com", "tokenpass")
        result = login_user(db, "tokenuser", "tokenpass")
        decoded = decode_token(result["access_token"])
        assert decoded["sub"] == "tokenuser"
        assert "user_id" in decoded


# ─── Tests de get_user_by_id ──────────────────────────────────────────────────

class TestGetUserById:
    def test_get_existing_user(self, db):
        """get_user_by_id debe retornar el usuario correcto."""
        user = register_user(db, "byid_user", "byid@example.com", "pass")
        found = get_user_by_id(db, user.id)
        assert found is not None
        assert found.username == "byid_user"

    def test_get_nonexistent_user_returns_none(self, db):
        """get_user_by_id con ID inexistente debe retornar None."""
        result = get_user_by_id(db, 9999)
        assert result is None
