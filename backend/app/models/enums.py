"""Перечисления PostgreSQL (create_type=False: их создаёт Alembic)."""

from enum import StrEnum

from sqlalchemy.dialects.postgresql import ENUM


class CallDirection(StrEnum):
    inbound = "inbound"
    outbound = "outbound"
    internal = "internal"
    tandem = "tandem"
    unknown = "unknown"


class CallDisposition(StrEnum):
    answered = "answered"
    abandoned = "abandoned"
    busy = "busy"
    no_answer = "no_answer"
    failed = "failed"
    transferred = "transferred"
    conferenced = "conferenced"
    other = "other"


class PbxKind(StrEnum):
    cm = "cm"
    ipo = "ipo"
    session_manager = "session_manager"
    sbce = "sbce"
    other = "other"


class LogKind(StrEnum):
    sip = "sip"
    e1 = "e1"
    alarm = "alarm"
    sat = "sat"
    other = "other"


call_direction_enum = ENUM(
    *[m.value for m in CallDirection],
    name="call_direction",
    create_type=False,
)
call_disposition_enum = ENUM(
    *[m.value for m in CallDisposition],
    name="call_disposition",
    create_type=False,
)
pbx_kind_enum = ENUM(
    *[m.value for m in PbxKind],
    name="pbx_kind",
    create_type=False,
)
log_kind_enum = ENUM(
    *[m.value for m in LogKind],
    name="log_kind",
    create_type=False,
)
