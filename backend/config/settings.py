import os

from dotenv import load_dotenv

load_dotenv()


def _cors_origins():
    raw = os.environ.get("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return "*"
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _database_connection_config():
    """Return a SQLAlchemy URL and PyMySQL-safe connection options.

    Aiven may provide a URL containing ``ssl-mode=REQUIRED``. That option is
    a MySQL CLI/connector option, not a valid PyMySQL ``connect()`` keyword.
    Passing it through SQLAlchemy causes: ``unexpected keyword argument
    'ssl-mode'``. Remove it from the URL and express TLS through PyMySQL's
    supported ``ssl`` connect argument instead.
    """
    from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

    raw_url = os.environ.get("DATABASE_URL", "").strip()
    if not raw_url:
        return None, {}

    # Normalize provider URLs when they use mysql:// but PyMySQL is the driver.
    if raw_url.startswith("mysql://"):
        raw_url = "mysql+pymysql://" + raw_url[len("mysql://"):]

    parsed = urlsplit(raw_url)
    query_items = parse_qsl(parsed.query, keep_blank_values=True)
    cleaned_query = []
    ssl_required = False

    for key, value in query_items:
        normalized_key = key.lower().replace("_", "-")
        if normalized_key == "ssl-mode":
            ssl_required = value.strip().lower() in {
                "required", "verify-ca", "verify-identity"
            }
            continue
        cleaned_query.append((key, value))

    clean_url = urlunsplit((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        urlencode(cleaned_query),
        parsed.fragment,
    ))

    # Aiven requires TLS. PyMySQL expects an ``ssl`` argument rather than
    # MySQL's ``ssl-mode`` URL query parameter.
    connect_args = {
        "ssl": {"check_hostname": False}
    } if ssl_required else {}

    return clean_url, connect_args


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "oto-yikama-demo-secret-change-me")
    DATABASE_URL, DATABASE_CONNECT_ARGS = _database_connection_config()
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 10,
        "connect_args": DATABASE_CONNECT_ARGS,
    }
    CORS_ORIGINS = _cors_origins()
