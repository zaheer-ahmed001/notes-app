import os

class Config:
    DB_USER = os.environ.get("DB_USER", "notesuser")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "notespass")
    DB_HOST = os.environ.get("DB_HOST", "postgres-service")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_NAME = os.environ.get("DB_NAME", "notesdb")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
