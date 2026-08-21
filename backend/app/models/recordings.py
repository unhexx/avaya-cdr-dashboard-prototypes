"""Метаданные записей; байты аудио в файлах, не в PostgreSQL."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RecordingMeta(Base):
    __tablename__ = "recording_meta"
    __table_args__ = (
        Index("idx_rec_ucid", "ucid"),
        Index("idx_rec_time", "start_time"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ucid: Mapped[str | None] = mapped_column(String(32))
    cdr_id: Mapped[int | None] = mapped_column(ForeignKey("cdr_records.id"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    calling_number: Mapped[str | None] = mapped_column(String(32))
    dialed_number: Mapped[str | None] = mapped_column(String(64))
    filename: Mapped[str | None] = mapped_column(String(512))
    mime_type: Mapped[str | None] = mapped_column(String(64))
    encrypted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    encryption_hint: Mapped[str | None] = mapped_column(String(64))
    sql_source_id: Mapped[str | None] = mapped_column(String(64))
    extra: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)

    cdr = relationship("CdrRecord", back_populates="recordings")
