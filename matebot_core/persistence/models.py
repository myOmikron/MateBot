"""
MateBot core database models
"""

import datetime

from sqlalchemy import (
    Boolean, DateTime, Integer, String,
    Column, FetchedValue, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


def _make_id_column():
    return Column(
        Integer,
        nullable=False,
        primary_key=True,
        autoincrement=True,
        unique=True
    )


class User(Base):
    __tablename__ = "users"

    id: int = _make_id_column()

    balance: int = Column(
        Integer,
        nullable=False,
        default=0
    )
    permission: bool = Column(
        Boolean,
        nullable=False,
        default=False
    )
    active: bool = Column(
        Boolean,
        nullable=False,
        default=True
    )
    created: datetime.datetime = Column(
        DateTime,
        server_default=func.now()
    )
    accessed: datetime.datetime = Column(
        DateTime,
        server_onupdate=FetchedValue(),
        server_default=func.now(),
        onupdate=func.now()
    )

    aliases = relationship(
        "UserAlias",
        cascade="all,delete",
        backref="user"
    )


class Application(Base):
    __tablename__ = "applications"

    id: int = _make_id_column()

    name: str = Column(
        String(255),
        nullable=False
    )

    aliases = relationship(
        "UserAlias",
        cascade="all,delete",
        backref="app"
    )


class UserAlias(Base):
    __tablename__ = "aliases"

    id: int = _make_id_column()

    user_id: int = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    app_id: int = Column(
        Integer,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False
    )
    username: str = Column(
        String(255)
    )
    first_name: str = Column(
        String(255)
    )
    last_name: str = Column(
        String(255)
    )
    app_user_id: str = Column(
        String(255),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("app_id", "app_user_id"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: int = _make_id_column()

    # TODO: reference to user ID
    sender: int = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    # TODO: reference to user ID
    receiver: int = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    amount: int = Column(
        Integer,
        nullable=False
    )
    reason: str = Column(
        String(255),
        nullable=True
    )
    registered: datetime.datetime = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
