import hashlib
import logging
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def _derive_key(secret_value: str) -> bytes:
    return hashlib.sha256(secret_value.encode("utf-8")).digest()


def _test_database_uri(uri: str, timeout: int = 5) -> bool:
    """Try to create a short-lived connection to the provided SQLAlchemy URI.

    Returns True when a connection succeeds, False otherwise. Any exceptions are
    swallowed and logged for diagnostics.
    """
    try:
        # Lazy import to avoid heavy dependencies at module import time when not needed
        from sqlalchemy import create_engine

        engine = create_engine(uri, connect_args={"connect_timeout": timeout})
        conn = engine.connect()
        conn.close()
        engine.dispose()
        return True
    except Exception as exc:  # pragma: no cover - diagnostics path
        # Use debug logging so a failed connection does not spam warnings on startup
        logging.getLogger("config").debug("Database connection test failed: %s", exc)
        return False


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Prefer explicit DATABASE_URL from environment; fall back to local MySQL URL used
    # during development. If the configured URL cannot be reached, fall back to
    # a file-based SQLite database to avoid startup-time crashes.
    _env_db = os.getenv(
        "DATABASE_URL",
        "mysql+mysqlconnector://root:password@localhost/encrypted_dbms",
    )

    if _env_db and _test_database_uri(_env_db):
        SQLALCHEMY_DATABASE_URI = _env_db
    else:
        # Fallback to a local sqlite file so the app can start without a working
        # MySQL server or valid credentials. Use an absolute path inside the
        # project directory to avoid "unable to open database file" errors.
        base_dir = os.path.abspath(os.path.dirname(__file__))
        sqlite_rel = os.getenv("SQLITE_FALLBACK", os.path.join("data", "encrypted_dbms.sqlite3"))
        # If SQLITE_FALLBACK was provided as a full URI (starts with sqlite:), respect it
        if sqlite_rel.startswith("sqlite:"):
            SQLALCHEMY_DATABASE_URI = sqlite_rel
        else:
            sqlite_path = os.path.join(base_dir, sqlite_rel)
            # Ensure the directory exists
            try:
                os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
            except Exception:
                pass
            # Use forward slashes in the URI on Windows
            uri_path = sqlite_path.replace('\\', '/')
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{uri_path}"

        logging.getLogger("config").debug("Using fallback DB URL: %s", SQLALCHEMY_DATABASE_URI)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8
    AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "0") == "1"
    ENCRYPTION_KEY = _derive_key(os.getenv("ENCRYPTION_SECRET", SECRET_KEY))
