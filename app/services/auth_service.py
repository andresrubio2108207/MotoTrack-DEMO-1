"""Servicio de autenticación: registro, login, JWT y logout."""

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User

# Configuración de hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY", "mototrack_demo_secret_key_2024")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def hash_password(password: str) -> str:
    """Genera el hash bcrypt de una contraseña."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contraseña coincida con su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un token JWT firmado."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decodifica y valida un token JWT. Retorna None si es inválido."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def register_user(db: Session, username: str, email: str, password: str) -> User:
    """
    Registra un nuevo usuario en la base de datos.

    Raises:
        ValueError: Si el username o email ya están en uso.
    """
    if db.query(User).filter(User.username == username).first():
        raise ValueError(f"El nombre de usuario '{username}' ya está en uso.")
    if db.query(User).filter(User.email == email).first():
        raise ValueError(f"El email '{email}' ya está registrado.")

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(db: Session, username: str, password: str) -> dict:
    """
    Autentica un usuario y retorna sus datos junto con un token JWT.

    Raises:
        ValueError: Si las credenciales son incorrectas.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Credenciales incorrectas. Verifica tu usuario y contraseña.")

    token = create_access_token({"sub": user.username, "user_id": user.id})
    return {"user": user, "access_token": token, "token_type": "bearer"}


def logout():
    """
    Cierra la sesión del usuario actual.
    En esta demo se limpia el estado de sesión (ver session_state.py).
    """
    from app.state.session_state import session_state
    session_state.clear()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Obtiene un usuario por su ID."""
    return db.query(User).filter(User.id == user_id).first()
