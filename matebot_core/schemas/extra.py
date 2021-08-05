"""
MateBot extra schemas

This module contains the special schemas for updates and the status.
"""

import sys
import time
import uuid
import datetime

import pydantic


class Updates(pydantic.BaseModel):
    aliases: uuid.UUID
    applications: uuid.UUID
    ballots: uuid.UUID
    communisms: uuid.UUID
    consumables: uuid.UUID
    refunds: uuid.UUID
    transactions: uuid.UUID
    users: uuid.UUID
    votes: uuid.UUID
    timestamp: pydantic.NonNegativeInt


class VersionInfo(pydantic.BaseModel):
    major: pydantic.PositiveInt
    minor: pydantic.NonNegativeInt
    micro: pydantic.NonNegativeInt


class Status(pydantic.BaseModel):
    healthy: bool
    startup: pydantic.NonNegativeInt = int(datetime.datetime.now().timestamp())
    api_version: VersionInfo
    project_version: VersionInfo
    python_version: VersionInfo = VersionInfo(
        major=sys.version_info.major,
        minor=sys.version_info.minor,
        micro=sys.version_info.micro
    )
    timezone: str = time.localtime().tm_zone
    localtime: datetime.datetime
    timestamp: pydantic.NonNegativeInt
