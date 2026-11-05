import os
import secrets
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DEBUG = True
TESTING = False

SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

WTF_CSRF_ENABLED = True

PRODUCTS_DB = BASE_DIR / "data" / "products.json"
CONTACT_LOG = BASE_DIR / "logs" / "contacts.log"

PRODUCT_UPLOAD_FOLDER = (
    BASE_DIR / "app" / "products" / "static" / "uploads"
)

MAX_CONTENT_LENGTH = 3 * 1024 * 1024