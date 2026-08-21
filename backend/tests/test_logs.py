"""Парсеры syslog SIP/E1 и GET /api/logs по фикстурам."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from app.parsers.syslog_e1 import parse_e1_line, parse_e1_text
from app.parsers.syslog_sip import parse_sip_line, parse_sip_text
from app.services.logs import ingest_log_fixtures, list_logs, load_fixture_logs

FIXTURES = Path(__file__).resolve().parents[2] / "docs" / "fixtures" / "syslog"


def test_parse_sip_fixture_invite_and_busy() -> None:
    text = (FIXTURES / "sip.log").read_text(encoding="utf-8")
    rows = parse_sip_text(text)
    assert len(rows) == 8
    invite = rows[0]
    assert invite.kind == "sip"
    assert invite.sip_method == "INVITE"
    assert invite.call_id == "c7f1abcd@sm.local"
    assert invite.host == "session-manager-01"
    busy = next(r for r in rows if r.sip_response == 486)
    assert busy.call_id == "busy-10010@sm.local"
    fail = next(r for r in rows if r.sip_response == 503)
    assert fail.severity == "err"


def test_parse_e1_fixture_los_and_slip() -> None:
    text = (FIXTURES / "e1.log").read_text(encoding="utf-8")
    rows = parse_e1_text(text)
    assert len(rows) == 7
    los = rows[0]
    assert los.kind == "e1"
    assert los.ds1_board == "01A0517"
    assert los.alarm_type == "LOS"
    assert los.host == "medpro-01"
    slip = next(r for r in rows if r.alarm_type == "SLIP")
    assert "CRC=12" in slip.message


def test_load_fixture_logs_both_kinds() -> None:
    rows = load_fixture_logs()
    kinds = {r.kind for r in rows}
    assert "sip" in kinds
    assert "e1" in kinds
    assert len(rows) == 15


def test_list_logs_filters() -> None:
    sip = list_logs(kind="sip")
    assert sip["total"] == 8
    assert all(i["kind"] == "sip" for i in sip["items"])
    e1 = list_logs(kind="e1")
    assert e1["total"] == 7
    by_call = list_logs(kind="sip", call_id="c7f1abcd")
    assert by_call["total"] == 5
    by_q = list_logs(kind="e1", q="RAI")
    assert by_q["total"] == 2
    alarm = list_logs(kind="alarm")
    assert alarm["total"] == 0


def test_api_logs_kind_sip_and_e1() -> None:
    client = TestClient(create_app())
    sip = client.get("/api/logs", params={"kind": "sip"})
    assert sip.status_code == 200
    body = sip.json()
    assert body["total"] == 8
    assert body["items"][0]["call_id"] is not None or body["items"][0]["sip_method"]
    e1 = client.get("/api/logs", params={"kind": "e1"})
    assert e1.status_code == 200
    assert e1.json()["total"] == 7
    assert e1.json()["items"][0]["ds1_board"]


def test_api_logs_openapi() -> None:
    client = TestClient(create_app())
    spec = client.get("/api/openapi.json").json()
    assert "/api/logs" in spec["paths"]


def test_ingest_log_fixtures_counts() -> None:
    stats = ingest_log_fixtures()
    assert stats["logs"] == 15
    assert stats["logs_sip"] == 8
    assert stats["logs_e1"] == 7


def test_sbce_sip_line() -> None:
    raw = (
        "<134>1 2026-08-21T14:31:10.200Z sbce-01 SIP: INVITE "
        "sip:84951234001@itsp.example SIP/2.0 Call-ID: out-10003@sbce.local CSeq: 1 INVITE"
    )
    ev = parse_sip_line(raw)
    assert ev is not None
    assert ev.host == "sbce-01"
    assert ev.sip_method == "INVITE"
    assert ev.call_id == "out-10003@sbce.local"


def test_e1_cleared_line() -> None:
    raw = "<134>Aug 21 14:10:08 medpro-01 DS1 01A0517 LOS cleared"
    ev = parse_e1_line(raw)
    assert ev is not None
    assert ev.alarm_type == "LOS"
    assert ev.severity == "info"
