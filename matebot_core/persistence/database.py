"""
MateBot database bindings and functions using sqlalchemy
"""

import sys
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine as _Engine
from sqlalchemy.orm import declarative_base, sessionmaker


DEFAULT_DATABASE_URL = "sqlite://"
Base = declarative_base()
_engine: Optional[_Engine] = None
_make_session: Optional[sessionmaker] = None


def init(database_url: str, echo: bool = True, create_all: bool = True):
    """
    Initialize the database bindings

    This function should be called at a very early program stage, before
    any part of it tries to access the database. If this isn't done,
    a temporary database will be used instead, which may be useful for
    debugging, too. See the ``DEFAULT_DATABASE_URL`` constant for details
    about the default connection. Without initialization prior to database
    usage, a warning will be emitted once to prevent future errors.

    :param database_url: the full URL to connect to the database
    :param echo: whether all SQLAlchemy magic should print to screen
    :param create_all: whether the metadata of the declarative base should
        be used to create all non-existing tables in the database
    """

    global _engine, _make_session
    if database_url.startswith("sqlite:"):
        if ":memory:" in database_url or database_url == "sqlite://":
            print(
                "Using the in-memory sqlite3 may lead to later problems. "
                "It's therefore recommended to create a persistent file.",
                file=sys.stderr
            )

        _engine = create_engine(
            database_url,
            echo=echo,
            connect_args={"check_same_thread": False}
        )

    else:
        _engine = create_engine(
            database_url,
            echo=echo
        )

    if create_all:
        Base.metadata.create_all(bind=_engine)

    _make_session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _warn(obj: str):
    print(
        f"Database {obj} not initialized! Using default database URL with database "
        f"{DEFAULT_DATABASE_URL!r}. Call 'init' once at program startup to fix "
        f"future problems due to non-persistent database and suppress this warning.",
        file=sys.stderr
    )


def get_engine() -> _Engine:
    if _engine is None:
        _warn("engine")
        init(DEFAULT_DATABASE_URL)
    return _engine


def get_new_session():
    if _make_session is None or _engine is None:
        _warn("engine or its session maker")
        init(DEFAULT_DATABASE_URL)
    return _make_session()
