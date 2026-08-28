import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv

load_dotenv()


def _cors_origins():
    raw = os.environ.get("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return "*"
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _database_url():
    """Normalize the managed MySQL URL for SQLAlchemy + PyMySQL.

    Aiven's MySQL URI can contain `ssl-mode=REQUIRED`. That option is not a
    valid PyMySQL keyword, so it must not be forwarded as a DBAPI argument.
    Aiven already provides TLS on the service; the URI is normalized here and
    the driver receives only parameters it understands.
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return None

    if url.startswith("mysql://"):
        url = "mysql+pymysql://" + url[len("mysql://"):]
    elif url.startswith("mysql+pymysql://"):
        pass
    else:
        return url

    parts = urlsplit(url)
    query = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        normalized = key.lower().replace("_", "-")
        # `ssl-mode` is a MySQL CLI/connector option, not a PyMySQL connect()
        # keyword. Keeping it in the URL causes TypeError at runtime.
        if normalized in {"ssl-mode", "sslmode"}:
            continue
        query.append((key, value))

    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    DATABASE_URL = _database_url()
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 10,
        "pool_size": 1,
        "max_overflow": 0,
    }
    CORS_ORIGINS = _cors_origins()
