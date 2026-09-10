import os

class Settings:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'tasks.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-task-manager-123")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")

    # Configurações SMTP seguras isoladas do código
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "taskmanager@gmail.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "dev-smtp-mock-password")

settings = Settings()
