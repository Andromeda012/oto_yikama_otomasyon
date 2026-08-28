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
    # The application deliberately has no localhost/default MySQL fallback.
    # Production uses an external/managed MySQL connection supplied by Vercel.
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return None

    # Normalize provider URLs when they use mysql:// but PyMySQL is the driver.
    if url.startswith("mysql://"):
        url = "mysql+pymysql://" + url[len("mysql://"): ]

    # Aiven may provide ?ssl-mode=REQUIRED in its URI.
    # PyMySQL does not accept "ssl-mode" as a DBAPI keyword, so remove it
    # from the URL and enable TLS through SQLAlchemy's connect_args instead.
    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    query = [(key, value) for key, value in query if key.lower() != "ssl-mode"]
    url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    DATABASE_URL = _database_url()
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"ssl": {}},
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 10,
    }
    CORS_ORIGINS = _cors_origins()
