"""Add images and machine_runtimes tables.

Revision ID: 001
Revises: None
Create Date: 2026-09-18
"""
from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create labs, jobs, images, and machine_runtimes tables."""
    op.create_table(
        "labs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("configuration", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "lab_id", sa.String(), sa.ForeignKey("labs.id"), nullable=False
        ),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("exit_code", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("logs", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "images",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("format", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column(
            "architecture", sa.String(), nullable=False, server_default="x86_64"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "machine_runtimes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "lab_id", sa.String(), sa.ForeignKey("labs.id"), nullable=False
        ),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_machine_id", sa.String(), nullable=False),
        sa.Column("provider_machine_name", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("runtime_path", sa.String(), nullable=True),
        sa.Column("serial_log", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop all tables created in this migration."""
    op.drop_table("machine_runtimes")
    op.drop_table("images")
    op.drop_table("jobs")
    op.drop_table("labs")
