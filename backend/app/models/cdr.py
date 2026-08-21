"""Канонические CDR: нормализованная строка плюс raw_record."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import call_direction_enum, call_disposition_enum


class CdrRecord(Base):
    __tablename__ = "cdr_records"
    __table_args__ = (
        UniqueConstraint("source_system", "raw_hash", name="uq_cdr_dedupe"),
        Index("idx_cdr_start_time", "start_time"),
        Index("idx_cdr_calling", "calling_number"),
        Index("idx_cdr_dialed", "dialed_number"),
        Index("idx_cdr_direction", "direction"),
        Index("idx_cdr_disposition", "disposition"),
        Index("idx_cdr_vdn", "vdn"),
        Index("idx_cdr_agent", "agent_extension"),
        Index("idx_cdr_ucid", "ucid"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ucid: Mapped[str | None] = mapped_column(String(32))
    call_id: Mapped[str | None] = mapped_column(String(32))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    answer_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ring_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hold_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    park_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_duration_seconds: Mapped[int] = mapped_column(
        Integer,
        Computed(
            "duration_seconds + ring_duration_seconds"
            " + COALESCE(hold_duration_seconds, 0)"
            " + COALESCE(park_duration_seconds, 0)",
            persisted=True,
        ),
    )
    calling_number: Mapped[str | None] = mapped_column(String(32))
    dialed_number: Mapped[str | None] = mapped_column(String(64))
    connected_number: Mapped[str | None] = mapped_column(String(64))
    direction: Mapped[str] = mapped_column(call_direction_enum, nullable=False, default="unknown")
    disposition: Mapped[str] = mapped_column(call_disposition_enum, nullable=False, default="other")
    condition_code: Mapped[str | None] = mapped_column(String(8))
    access_code_dialed: Mapped[str | None] = mapped_column(String(8))
    access_code_used: Mapped[str | None] = mapped_column(String(8))
    trunk_in: Mapped[str | None] = mapped_column(String(16))
    trunk_out: Mapped[str | None] = mapped_column(String(16))
    account_code: Mapped[str | None] = mapped_column(String(32))
    auth_code: Mapped[str | None] = mapped_column(String(16))
    vdn: Mapped[str | None] = mapped_column(String(16))
    node_number: Mapped[str | None] = mapped_column(String(8))
    agent_extension: Mapped[str | None] = mapped_column(String(16))
    agent_id: Mapped[str | None] = mapped_column(String(16))
    skill_group: Mapped[str | None] = mapped_column(String(16))
    is_internal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_transferred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_conferenced: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_system: Mapped[str] = mapped_column(String(64), nullable=False, default="mock")
    pbx_node_id: Mapped[int | None] = mapped_column(ForeignKey("pbx_nodes.id"))
    raw_record: Mapped[str | None] = mapped_column(Text)
    raw_hash: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    pbx_node = relationship("PbxNode", back_populates="cdr_records")
    recordings = relationship("RecordingMeta", back_populates="cdr")
