"""SQLAlchemy ORM models for Kernel Lab."""

from __future__ import annotations

import datetime

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class LabModel(Base):
    """SQLAlchemy model for a Lab."""

    __tablename__ = "labs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    configuration: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=datetime.datetime.now(datetime.UTC)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=datetime.datetime.now(datetime.UTC)
    )


class JobModel(Base):
    """SQLAlchemy model for a Job."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    lab_id: Mapped[str] = mapped_column(String, ForeignKey("labs.id"), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=datetime.datetime.now(datetime.UTC)
    )
    started_at: Mapped[datetime.datetime | None] = mapped_column(nullable=True)
    finished_at: Mapped[datetime.datetime | None] = mapped_column(nullable=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    logs: Mapped[str | None] = mapped_column(Text, nullable=True)


class ImageModel(Base):
    """SQLAlchemy model for an Image."""

    __tablename__ = "images"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    format: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    architecture: Mapped[str] = mapped_column(String, nullable=False, default="x86_64")
    created_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=datetime.datetime.now(datetime.UTC)
    )
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class MachineRuntimeModel(Base):
    """SQLAlchemy model for a Machine Runtime (VM runtime state)."""

    __tablename__ = "machine_runtimes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    lab_id: Mapped[str] = mapped_column(String, ForeignKey("labs.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    provider_machine_id: Mapped[str] = mapped_column(String, nullable=False)
    provider_machine_name: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    runtime_path: Mapped[str | None] = mapped_column(String, nullable=True)
    serial_log: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=datetime.datetime.now(datetime.UTC)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False, default=datetime.datetime.now(datetime.UTC)
    )
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
