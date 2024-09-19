from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class CeleryTaskMeta(SQLModel, table=True):
    __tablename__ = "celery_taskmeta"  # Explicit table name

    id: int = Field(default=None, primary_key=True)
    task_id: str = Field(
        sa_column_kwargs={"nullable": True, "unique": True}, max_length=155
    )
    status: Optional[str] = Field(default=None, max_length=50, nullable=True)
    result: Optional[bytes] = Field(nullable=True)
    date_done: Optional[datetime] = Field(nullable=True)
    traceback: Optional[str] = Field(nullable=True)
    name: Optional[str] = Field(default=None, max_length=155, nullable=True)
    args: Optional[bytes] = Field(nullable=True)
    kwargs: Optional[bytes] = Field(nullable=True)
    worker: Optional[str] = Field(default=None, max_length=155, nullable=True)
    retries: Optional[int] = Field(nullable=True)
    queue: Optional[str] = Field(default=None, max_length=155, nullable=True)


class CeleryTaskSetMeta(SQLModel, table=True):
    __tablename__ = "celery_tasksetmeta"  # Specify the table name explicitly

    id: int = Field(default=None, primary_key=True)
    taskset_id: str = Field(
        sa_column_kwargs={"nullable": True, "unique": True}, max_length=155
    )
    result: Optional[bytes] = Field(nullable=True)
    date_done: Optional[datetime] = Field(nullable=True)
