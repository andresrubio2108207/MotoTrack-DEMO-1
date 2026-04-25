"""Configuración del motor de base de datos SQLite."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL de la base de datos desde variable de entorno o valor por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mototrack.db")

# Crear el motor SQLite con soporte de hilos habilitado
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Generador de sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa la base de datos creando todas las tablas."""
    from app.database.base import Base
    # Importar modelos para que SQLAlchemy los registre
    from app.models import user, motorcycle, maintenance, alert  # noqa: F401
    Base.metadata.create_all(bind=engine)
