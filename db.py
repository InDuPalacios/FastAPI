from fastapi import FastAPI, Depends
from typing import Annotated
from sqlmodel import Session, create_engine, SQLModel


# SQLite database configuration
sqlite_name = "db.sqlite3"
sqlite_url = f"sqlite:///{sqlite_name}"


# Create database engine
engine = create_engine(sqlite_url)


def create_all_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


def get_session():
    """
    Dependency function to get a SQLModel session.
    Ensures that the session is properly opened and closed.
    """
    with Session(engine) as session:
        yield session


# Annotated dependency to inject session into routes
SessionDep = Annotated[Session, Depends(get_session)]
