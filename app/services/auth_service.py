from __future__ import annotations

from typing import Any

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from app.database.engine import session_scope
from app.models import Motorcycle, User


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return plain_password == hashed_password


def get_user_by_id(user_id: int) -> User | None:
    with session_scope() as session:
        return session.get(User, user_id)


def get_user_by_email(email: str) -> User | None:
    normalized_email = email.strip().lower()
    with session_scope() as session:
        return session.query(User).filter(User.email == normalized_email).first()


def list_users() -> list[User]:
    with session_scope() as session:
        return session.query(User).order_by(User.created_at.desc()).all()


def register_user(name: str, email: str, password: str) -> User:
    normalized_email = email.strip().lower()

    with session_scope() as session:
        existing_user = session.query(User).filter(User.email == normalized_email).first()
        if existing_user is not None:
            raise ValueError("Ya existe un usuario registrado con ese correo.")

        user = User(
            name=name.strip(),
            email=normalized_email,
            password=hash_password(password),
        )
        session.add(user)
        session.flush()
        session.refresh(user)
        return user


def authenticate_user(email: str, password: str) -> User | None:
    normalized_email = email.strip().lower()

    with session_scope() as session:
        user = session.query(User).filter(User.email == normalized_email).first()
        if user is None or not verify_password(password, user.password):
            return None
        if user.password == password:
            user.password = hash_password(password)
            session.flush()
            session.refresh(user)
        return user


def add_motorcycle(
    user_id: int,
    brand: str,
    model: str,
    year: int,
    plate: str,
    current_km: float = 0.0,
) -> Motorcycle:
    normalized_plate = plate.strip().upper()

    with session_scope() as session:
        user = session.get(User, user_id)
        if user is None:
            raise ValueError("El usuario no existe.")

        existing_plate = session.query(Motorcycle).filter(Motorcycle.plate == normalized_plate).first()
        if existing_plate is not None:
            raise ValueError("La placa ya está registrada.")

        motorcycle = Motorcycle(
            user_id=user_id,
            brand=brand.strip(),
            model=model.strip(),
            year=int(year),
            plate=normalized_plate,
            current_km=float(current_km),
        )
        session.add(motorcycle)
        session.flush()
        session.refresh(motorcycle)
        return motorcycle


def list_user_motorcycles(user_id: int) -> list[Motorcycle]:
    with session_scope() as session:
        return (
            session.query(Motorcycle)
            .filter(Motorcycle.user_id == user_id)
            .order_by(Motorcycle.created_at.desc())
            .all()
        )


def get_motorcycle(motorcycle_id: int, user_id: int | None = None) -> Motorcycle | None:
    with session_scope() as session:
        query = session.query(Motorcycle).filter(Motorcycle.id == motorcycle_id)
        if user_id is not None:
            query = query.filter(Motorcycle.user_id == user_id)
        return query.first()


def update_motorcycle(motorcycle_id: int, **changes: Any) -> Motorcycle:
    with session_scope() as session:
        motorcycle = session.get(Motorcycle, motorcycle_id)
        if motorcycle is None:
            raise ValueError("La motocicleta no existe.")

        for field in ("brand", "model", "year", "current_km"):
            if field in changes and changes[field] is not None:
                setattr(motorcycle, field, changes[field])

        if "plate" in changes and changes["plate"]:
            normalized_plate = str(changes["plate"]).strip().upper()
            duplicate = (
                session.query(Motorcycle)
                .filter(Motorcycle.plate == normalized_plate, Motorcycle.id != motorcycle_id)
                .first()
            )
            if duplicate is not None:
                raise ValueError("La placa ya está registrada.")
            motorcycle.plate = normalized_plate

        session.flush()
        session.refresh(motorcycle)
        return motorcycle


def update_motorcycle_km(motorcycle_id: int, current_km: int | float) -> Motorcycle:
    return update_motorcycle(motorcycle_id, current_km=float(current_km))


def delete_motorcycle(motorcycle_id: int) -> bool:
    with session_scope() as session:
        motorcycle = session.get(Motorcycle, motorcycle_id)
        if motorcycle is None:
            return False
        session.delete(motorcycle)
        return True
