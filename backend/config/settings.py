import os

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
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "oto-yikama-demo-secret-change-me")
    DATABASE_URL = _database_url()
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 10,
    }
    CORS_ORIGINS = _cors_origins()
