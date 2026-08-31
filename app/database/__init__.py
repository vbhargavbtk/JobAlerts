"""
Database package initialization
"""
from app.database.connection import engine, AsyncSessionLocal, init_db, get_db
from app.database.models import (
    Base,
    Channel,
    ProcessedMessage,
    Job,
    Source,
    Alert,
    Failure,
    UserRequirement,
    utc_now,
    generate_uuid
)
from app.database.repository import DatabaseRepository

__all__ = [
    "engine",
    "AsyncSessionLocal",
    "init_db",
    "get_db",
    "Base",
    "Channel",
    "ProcessedMessage",
    "Job",
    "Source",
    "Alert",
    "Failure",
    "UserRequirement",
    "DatabaseRepository",
    "utc_now",
    "generate_uuid"
]
