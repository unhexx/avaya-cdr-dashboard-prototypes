"""Парсеры текстовых дампов SAT: status health, display alarms, status ds1."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

# Команды v1: только чтение. change/add/busyout отбрасываются коннектором.
SAT_ALLOWLIST: tuple[str, ...] = (
    "status health",
    "display alarms",
    "status trunk",
    "status ds1",
    "list measurements occupancy",
    "list measurements ds1 summary",
    "list ars analysis",
    "display dialplan analysis",
    "list station",
    "list vdn",
    "list hunt-group",
    "status processor-channel",
    "display system-parameters cdr",
)

_SEVERITIES = ("critical", "major", "minor", "warning")
_PCT_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*%?")
_KV_RE = re.compile(r"^([^:]+):\s*(.+)$")


def normalize_sat_command(command: str) -> str:
    return " ".join(command.lower().split())


def is_sat_allowed(command: str) -> bool:
    """True, если команда (с аргументом вроде `status ds1 01A0517`) в allowlist."""
    normalized = normalize_sat_command(command)
    if not normalized:
        return False
    for allowed in SAT_ALLOWLIST:
        if normalized == allowed or normalized.startswith(allowed + " "):
            return True
    return False


def _pct(value: str) -> Decimal | None:
    match = _PCT_RE.search(value.replace(",", "."))
    if not match:
        return None
    try:
        return Decimal(match.group(1))
    except InvalidOperation:
        return None


def _int_token(value: str) -> int | None:
    match = re.search(r"-?\d+", value)
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


def _is_noise(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    lower = stripped.lower()
    if lower.startswith("command "):
        return True
    if set(stripped) <= {"-", "="}:
        return True
    return False


@dataclass
class ParsedSatHealth:
    occupancy_pct: Decimal | None = None
    idle_cpu_pct: Decimal | None = None
    system_management: str | None = None
    last_reload: str | None = None
    alarms_major: int = 0
    alarms_minor: int = 0
    alarms_warning: int = 0
    raw: str = ""

    @property
    def status(self) -> str:
        mgmt = (self.system_management or "").lower()
        if mgmt and mgmt not in {"up", "ok", "in-service"}:
            return "down"
        if self.alarms_major > 0:
            return "degraded"
        if self.alarms_minor > 0 or self.alarms_warning > 0:
            return "degraded"
        if self.occupancy_pct is None and not mgmt:
            return "unknown"
        return "ok"


@dataclass
class ParsedSatAlarm:
    port: str | None
    alt_name: str | None
    onboard: bool | None
    resource_type: str | None
    service_state: str | None
    severity: str
    message: str
    raw: str

    @property
    def resource(self) -> str:
        return self.port or self.alt_name or self.resource_type or "unknown"

    @property
    def code(self) -> str:
        kind = self.resource_type or "alarm"
        return f"{kind}-{self.severity}"


@dataclass
class ParsedDs1Status:
    location: str | None = None
    alarms: str | None = None
    slip_count: int | None = None
    misframe_count: int | None = None
    code: str | None = None
    framing: str | None = None
    signaling: str | None = None
    port_network: str | None = None
    raw: str = ""

    def as_details(self) -> dict[str, object]:
        return {
            "location": self.location,
            "alarms": self.alarms,
            "slip_count": self.slip_count,
            "misframe_count": self.misframe_count,
            "code": self.code,
            "framing": self.framing,
            "signaling": self.signaling,
            "port_network": self.port_network,
        }


@dataclass
class SatHealthBundle:
    """Снимок CM из набора SAT-фикстур."""

    health: ParsedSatHealth
    alarms: list[ParsedSatAlarm] = field(default_factory=list)
    ds1: list[ParsedDs1Status] = field(default_factory=list)


def parse_status_health(text: str) -> ParsedSatHealth:
    result = ParsedSatHealth(raw=text)
    for line in text.splitlines():
        if _is_noise(line):
            continue
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith("status health") or "system health" in lower:
            continue
        if lower.startswith("test") and "result" in lower:
            continue
        parts = re.split(r"\s{2,}", stripped)
        if len(parts) < 2:
            continue
        key = parts[0].strip().lower()
        value = parts[-1].strip()
        if "processor occupancy" in key:
            result.occupancy_pct = _pct(value)
        elif "idle cpu" in key:
            result.idle_cpu_pct = _pct(value)
        elif "system management" in key:
            result.system_management = value.lower()
        elif "last reload" in key:
            result.last_reload = value
        elif "alarms major" in key:
            result.alarms_major = _int_token(value) or 0
        elif "alarms minor" in key:
            result.alarms_minor = _int_token(value) or 0
        elif "alarms warning" in key:
            result.alarms_warning = _int_token(value) or 0
    return result


def parse_display_alarms(text: str) -> list[ParsedSatAlarm]:
    rows: list[ParsedSatAlarm] = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if _is_noise(line):
            continue
        lower = stripped.lower()
        if lower.startswith("display alarms") or "alarm report" in lower:
            continue
        if lower.startswith("port") and "alarm" in lower:
            in_table = True
            continue
        if not in_table:
            continue
        tokens = stripped.split()
        if len(tokens) < 5:
            continue
        onboard_idx = next(
            (i for i, tok in enumerate(tokens) if tok.lower() in {"y", "n"} and i > 0),
            None,
        )
        if onboard_idx is None or onboard_idx + 3 >= len(tokens):
            continue
        port = tokens[0]
        alt_name = " ".join(tokens[1:onboard_idx]) or None
        onboard = tokens[onboard_idx].lower() == "y"
        resource_type = tokens[onboard_idx + 1]
        service_state = tokens[onboard_idx + 2]
        rest = tokens[onboard_idx + 3 :]
        severity = "warning"
        message_parts = rest
        if rest and rest[0].lower() in _SEVERITIES:
            severity = rest[0].lower()
            message_parts = rest[1:]
        message = " ".join(message_parts) if message_parts else severity
        rows.append(
            ParsedSatAlarm(
                port=port,
                alt_name=alt_name,
                onboard=onboard,
                resource_type=resource_type,
                service_state=service_state,
                severity=severity,
                message=message,
                raw=stripped,
            )
        )
    return rows


def parse_status_ds1(text: str) -> ParsedDs1Status:
    result = ParsedDs1Status(raw=text)
    for line in text.splitlines():
        if _is_noise(line):
            continue
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith("status ds1") or "ds1 link status" in lower:
            continue
        match = _KV_RE.match(stripped)
        if not match:
            continue
        key = match.group(1).strip().lower()
        value = match.group(2).strip()
        if key == "location":
            result.location = value
        elif key == "alarms":
            result.alarms = value
        elif key == "slip count":
            result.slip_count = _int_token(value)
        elif key == "misframe count":
            result.misframe_count = _int_token(value)
        elif key == "code":
            result.code = value
        elif key == "framing":
            result.framing = value
        elif key == "signaling":
            result.signaling = value
        elif key == "port network":
            result.port_network = value
    return result


def parse_sat_bundle(
    health_text: str,
    alarms_text: str,
    ds1_texts: list[str] | None = None,
) -> SatHealthBundle:
    return SatHealthBundle(
        health=parse_status_health(health_text),
        alarms=parse_display_alarms(alarms_text),
        ds1=[parse_status_ds1(t) for t in (ds1_texts or [])],
    )
