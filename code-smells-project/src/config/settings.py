import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    DB_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "loja.db"))

settings = Settings()
