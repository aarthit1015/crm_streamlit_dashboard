import logging
import sys

# Create logger
logger = logging.getLogger("crm_logger")
logger.setLevel(logging.DEBUG)   # Use DEBUG to capture all details

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_format = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | "
    "%(filename)s:%(lineno)d | %(funcName)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(console_format)

# Avoid duplicate handlers on reload
if not logger.handlers:
    logger.addHandler(console_handler)

# Optional: file handler for persistent logs
file_handler = logging.FileHandler("crm_app.log", mode="a", encoding="utf-8")
file_handler.setFormatter(console_format)
logger.addHandler(file_handler)

