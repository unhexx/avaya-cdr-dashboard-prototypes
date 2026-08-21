"""Снимки здоровья АТС и журнал аварий."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class HealthSnapshot(Base):
    __tablename__ = "health_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pbx_node_id: Mapped[int] = mapped_column(ForeignKey("pbx_nodes.id"), nullable=False)
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    occupancy_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    details: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)

    pbx_node = relationship("PbxNode", back_populates="health_snapshots")


class Alarm(Base):
    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pbx_node_id: Mapped[int | None] = mapped_column(ForeignKey("pbx_nodes.id"))
    raised_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cleared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    code: Mapped[str | None] = mapped_column(String(32))
    resource: Mapped[str | None] = mapped_column(String(64))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    raw: Mapped[str | None] = mapped_column(Text)

    pbx_node = relationship("PbxNode", back_populates="alarms")
