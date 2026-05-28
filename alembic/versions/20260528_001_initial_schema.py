"""initial schema

Revision ID: 20260528_001
Revises:
Create Date: 2026-05-28
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260528_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_accounts",
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "groups",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "keywords",
        sa.Column("phrase", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phrase"),
    )

    op.create_table(
        "testers",
        sa.Column("member_no", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone_last4", sa.String(length=4), nullable=True),
        sa.Column("group_id", sa.String(length=36), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("member_no"),
    )

    op.create_table(
        "group_week_keyword_assignments",
        sa.Column("group_id", sa.String(length=36), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("keyword_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_admin_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["created_by_admin_id"], ["admin_accounts.id"]),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["keyword_id"], ["keywords.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", "week_start", "keyword_id", name="uq_group_week_keyword"),
    )

    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_by_admin_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["updated_by_admin_id"], ["admin_accounts.id"]),
        sa.PrimaryKeyConstraint("key"),
    )

    op.create_table(
        "search_attempt_logs",
        sa.Column("tester_id", sa.String(length=36), nullable=False),
        sa.Column("group_id", sa.String(length=36), nullable=True),
        sa.Column("keyword_id", sa.String(length=36), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("member_no_snapshot", sa.String(length=100), nullable=False),
        sa.Column("tester_name_snapshot", sa.String(length=100), nullable=False),
        sa.Column("group_name_snapshot", sa.String(length=100), nullable=True),
        sa.Column("keyword_snapshot", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["keyword_id"], ["keywords.id"]),
        sa.ForeignKeyConstraint(["tester_id"], ["testers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "warning_logs",
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("member_no", sa.String(length=100), nullable=True),
        sa.Column("request_path", sa.String(length=255), nullable=True),
        sa.Column("detail_json", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "admin_audit_logs",
        sa.Column("admin_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=True),
        sa.Column("detail_json", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["admin_id"], ["admin_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("admin_audit_logs")
    op.drop_table("warning_logs")
    op.drop_table("search_attempt_logs")
    op.drop_table("app_settings")
    op.drop_table("group_week_keyword_assignments")
    op.drop_table("testers")
    op.drop_table("keywords")
    op.drop_table("groups")
    op.drop_table("admin_accounts")
