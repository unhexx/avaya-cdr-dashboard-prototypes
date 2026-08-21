"""Узлы АТС (CM / IPO / SM / SBCE)."""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import pbx_kind_enum


class PbxNode(Base):
    __tablename__ = "pbx_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(pbx_kind_enum, nullable=False)
    host: Mapped[str | None] = mapped_column(String(255))
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    extra: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)

    cdr_records = relationship("CdrRecord", back_populates="pbx_node")
    health_snapshots = relationship("HealthSnapshot", back_populates="pbx_node")
    alarms = relationship("Alarm", back_populates="pbx_node")
    dialplan_entries = relationship("DialplanEntry", back_populates="pbx_node")
    log_events = relationship("LogEvent", back_populates="pbx_node")
