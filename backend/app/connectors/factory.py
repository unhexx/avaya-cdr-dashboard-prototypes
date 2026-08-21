"""Сборка пакета коннекторов. SysMonitor запрещён и не реализуется."""

from app.connectors.base import ProtocolConnector
from app.connectors.cm_cdr import CmCdrConnector
from app.connectors.cm_sat import CmSatConnector
from app.connectors.cm_snmp import CmSnmpConnector
from app.connectors.ipo_smdr import IpoSmdrConnector
from app.connectors.ipo_snmp import IpoSnmpConnector
from app.connectors.mock import MockConnector
from app.connectors.sql_source import SqlSourceConnector


def build_connectors() -> list[ProtocolConnector]:
    return [
        MockConnector(),
        CmCdrConnector(),
        CmSatConnector(),
        CmSnmpConnector(),
        IpoSmdrConnector(),
        IpoSnmpConnector(),
        SqlSourceConnector(),
    ]
