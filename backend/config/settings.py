import os

from dotenv import load_dotenv

load_dotenv()


def _cors_origins():
    raw = os.environ.get("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return "*"
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    DATABASE_URL = os.environ.get("DATABASE_URL", "mysql+pymysql://root:password@localhost/car_wash")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = _cors_origins()
