from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = f"sqlite:///{PROJECT_ROOT / 'mototrack.db'}"


def _read_database_url() -> str:
    return os.getenv("MOTOTRACK_DB_URL") or os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL


_database_url = _read_database_url()
_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite")


def _get_sqlite_file_path(database_url: str) -> Path | None:
    if not _is_sqlite_url(database_url):
        return None

    database_path = make_url(database_url).database
    if not database_path or database_path == ":memory:":
        return None

    return Path(database_path)


def _ensure_valid_sqlite_file(database_url: str) -> None:
    database_path = _get_sqlite_file_path(database_url)
    if database_path is None:
        return

    database_path.parent.mkdir(parents=True, exist_ok=True)
    if not database_path.exists() or database_path.stat().st_size == 0:
        return

    with database_path.open("rb") as file:
        header = file.read(16)

    if header == b"SQLite format 3\x00":
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = database_path.with_suffix(f"{database_path.suffix}.invalid_{timestamp}.bak")
    database_path.replace(backup_path)


def _build_engine(database_url: str) -> Engine:
    _ensure_valid_sqlite_file(database_url)
    connect_args = {"check_same_thread": False} if _is_sqlite_url(database_url) else {}
    engine = create_engine(database_url, connect_args=connect_args, future=True)

    if _is_sqlite_url(database_url):
        @event.listens_for(engine, "connect")
        def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def configure_database(database_url: str | None = None) -> str:
    global _database_url, _engine, _SessionLocal

    if _engine is not None:
        _engine.dispose()

    _database_url = database_url or _read_database_url()
    _engine = _build_engine(_database_url)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return _database_url


def get_database_url() -> str:
    return _database_url


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        configure_database(_database_url)
    return _engine


def get_session() -> Session:
    global _SessionLocal
    if _SessionLocal is None:
        configure_database(_database_url)
    return _SessionLocal()


@contextmanager
def session_scope() -> Iterator[Session]:
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(drop_existing: bool = False) -> None:
    import app.models  # noqa: F401

    engine = get_engine()
    if drop_existing:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def dispose_engine() -> None:
    global _engine, _SessionLocal

    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
