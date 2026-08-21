"""События syslog: SIP, E1/DS1, аварии SAT."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import log_kind_enum


class LogEvent(Base):
    __tablename__ = "log_events"
    __table_args__ = (
        Index("idx_log_time", "event_time"),
        Index("idx_log_kind", "kind", "event_time"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pbx_node_id: Mapped[int | None] = mapped_column(ForeignKey("pbx_nodes.id"))
    kind: Mapped[str] = mapped_column(log_kind_enum, nullable=False, default="other")
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    host: Mapped[str | None] = mapped_column(String(128))
    severity: Mapped[str | None] = mapped_column(String(16))
    call_id: Mapped[str | None] = mapped_column(String(64))
    sip_method: Mapped[str | None] = mapped_column(String(16))
    sip_response: Mapped[int | None] = mapped_column(Integer)
    ds1_board: Mapped[str | None] = mapped_column(String(32))
    alarm_type: Mapped[str | None] = mapped_column(String(16))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    raw: Mapped[str | None] = mapped_column(Text)

    pbx_node = relationship("PbxNode", back_populates="log_events")
