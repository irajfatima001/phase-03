from sqlmodel import SQLModel
from typing import List
import uuid
from datetime import datetime
from pydantic import BaseModel


class BaseSQLModel(SQLModel):
    """Base class for all SQLModels"""
    pass


def generate_uuid():
    return str(uuid.uuid4())


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime