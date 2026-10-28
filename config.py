import os
import secrets

DEBUG = True
TESTING = False

SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"