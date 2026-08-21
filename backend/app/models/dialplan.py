"""Снимок план нумерации (ARS / IPO), не realtime."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class DialplanEntry(Base):
    __tablename__ = "dialplan_entries"
    __table_args__ = (Index("idx_dialplan_prefix", "match_prefix"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pbx_node_id: Mapped[int | None] = mapped_column(ForeignKey("pbx_nodes.id"))
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    match_prefix: Mapped[str] = mapped_column(String(32), nullable=False)
    min_digits: Mapped[int | None] = mapped_column(Integer)
    max_digits: Mapped[int | None] = mapped_column(Integer)
    route: Mapped[str | None] = mapped_column(String(64))
    location: Mapped[str | None] = mapped_column(String(32))
    raw: Mapped[str | None] = mapped_column(Text)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    pbx_node = relationship("PbxNode", back_populates="dialplan_entries")
