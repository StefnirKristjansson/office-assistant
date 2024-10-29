"""Connections to database, and function to create database tables if they don't exist."""
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session


class DatabaseEngine:  # pylint: disable=too-few-public-methods
    """Database engine, it checks if the engine is already created, if not it creates it."""

    def __init__(self):
        self._engine = None

    def get_engine(self):
        """Get database engine."""
        if self._engine is None:
            load_dotenv()
            database_url = (
                "postgresql://"
                + os.environ["POSTGRES_USER"]
                + ":"
                + os.environ["POSTGRES_PASSWORD"]
                + "@"
                + os.environ["POSTGRES_SERVER"]
                + ":"
                + os.environ["POSTGRES_PORT"]
                + "/"
                + os.environ["POSTGRES_DB"]
            )
            self._engine = create_engine(database_url, echo=False, pool_timeout=30)
        return self._engine


db_engine = DatabaseEngine()


def get_engine():
    """Get database engine."""
    return db_engine.get_engine()


def create_db_and_tables():  # pragma: no cover
    """Create database and tables if they don't exist."""
    SQLModel.metadata.create_all(get_engine())


def get_session():  # pragma: no cover
    """Get session for database."""
    with Session(get_engine()) as session:
        yield session
