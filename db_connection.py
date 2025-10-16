from sqlalchemy import create_engine
import os
from urllib.parse import quote_plus
from logger_config import logger

DB_USER = os.getenv("DB_USER", "odoo")
DB_PASS = os.getenv("DB_PASS", "dev")
DB_HOST = os.getenv("DB_HOST", "172.188.13.193")
DB_PORT = os.getenv("DB_PORT", "9832")
DB_NAME = os.getenv("DB_NAME", "dev-es")

# ✅ Force pg8000 (do NOT use psycopg2)
DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    logger.info(f"Connected to DB: {DB_HOST}:{DB_PORT}/{DB_NAME}")
except Exception as e:
    logger.error(f"DB Connection Error: {e}")
    raise
