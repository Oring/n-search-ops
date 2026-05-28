from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AdminAccount(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "admin_accounts"

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    audit_logs: Mapped[list["AdminAuditLog"]] = relationship(back_populates="admin")


class Group(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    testers: Mapped[list["Tester"]] = relationship(back_populates="group")
    assignments: Mapped[list["GroupWeekKeywordAssignment"]] = relationship(back_populates="group")


class Keyword(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "keywords"

    phrase: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    assignments: Mapped[list["GroupWeekKeywordAssignment"]] = relationship(back_populates="keyword")


class Tester(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "testers"
    __test__ = False

    member_no: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    group_id: Mapped[str | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    group: Mapped[Group | None] = relationship(back_populates="testers")
    search_attempts: Mapped[list["SearchAttemptLog"]] = relationship(back_populates="tester")


class GroupWeekKeywordAssignment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "group_week_keyword_assignments"
    __table_args__ = (
        UniqueConstraint("group_id", "week_start", "keyword_id", name="uq_group_week_keyword"),
    )

    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    keyword_id: Mapped[str] = mapped_column(ForeignKey("keywords.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by_admin_id: Mapped[str | None] = mapped_column(ForeignKey("admin_accounts.id"), nullable=True)

    group: Mapped[Group] = relationship(back_populates="assignments")
    keyword: Mapped[Keyword] = relationship(back_populates="assignments")


class AppSetting(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_by_admin_id: Mapped[str | None] = mapped_column(ForeignKey("admin_accounts.id"), nullable=True)


class SearchAttemptLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "search_attempt_logs"

    tester_id: Mapped[str] = mapped_column(ForeignKey("testers.id"), nullable=False)
    group_id: Mapped[str | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    keyword_id: Mapped[str] = mapped_column(ForeignKey("keywords.id"), nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    member_no_snapshot: Mapped[str] = mapped_column(String(100), nullable=False)
    tester_name_snapshot: Mapped[str] = mapped_column(String(100), nullable=False)
    group_name_snapshot: Mapped[str | None] = mapped_column(String(100), nullable=True)
    keyword_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="app")

    tester: Mapped[Tester] = relationship(back_populates="search_attempts")
    group: Mapped[Group | None] = relationship()
    keyword: Mapped[Keyword] = relationship()


class WarningLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "warning_logs"

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    member_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    request_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detail_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AdminAuditLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "admin_audit_logs"

    admin_id: Mapped[str | None] = mapped_column(ForeignKey("admin_accounts.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    detail_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    admin: Mapped[AdminAccount | None] = relationship(back_populates="audit_logs")
