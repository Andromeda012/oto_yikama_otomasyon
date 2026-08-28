import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv

load_dotenv()


def _cors_origins():
    raw = os.environ.get("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return "*"
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _database_settings():
    """Return a SQLAlchemy URL plus PyMySQL connection arguments.

    Aiven supplies MySQL URLs containing ``ssl-mode=REQUIRED``. That is a
    MySQL client/CLI style option and must not be forwarded to PyMySQL as a
    keyword argument named ``ssl-mode``. We remove it from the URL and enable
    TLS through PyMySQL's supported ``ssl`` connection argument instead.
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return None, {}

    # Normalize provider URLs when they use mysql:// but PyMySQL is the driver.
    if url.startswith("mysql://"):
        url = "mysql+pymysql://" + url[len("mysql://"): ]

    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    cleaned_query = []
    ssl_required = False

    for key, value in query:
        normalized = key.lower().replace("_", "-")
        if normalized == "ssl-mode":
            ssl_required = value.upper() in {"REQUIRED", "VERIFY_CA", "VERIFY_IDENTITY"}
            continue
        cleaned_query.append((key, value))

    if query:
        url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(cleaned_query), parts.fragment))

    # PyMySQL accepts ``ssl`` but not ``ssl-mode``. An empty SSL dictionary
    # enables TLS negotiation using the driver's defaults.
    connect_args = {"ssl": {}} if ssl_required else {}
    return url, connect_args


DATABASE_URL, DATABASE_CONNECT_ARGS = _database_settings()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "oto-yikama-demo-secret-change-me")
    DATABASE_URL = DATABASE_URL
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 10,
        "connect_args": DATABASE_CONNECT_ARGS,
    }
    CORS_ORIGINS = _cors_origins()
