from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class TimeSeriesData(BaseModel):
    timestamp: datetime
    value: float
    label: Optional[str] = None


class MetricsSummary(BaseModel):
    total_packets: int
    total_alerts: int
    active_threats: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int
    packets_per_second: float
    bytes_per_second: float
    top_protocols: List[dict]
    top_source_ips: List[dict]
    top_destination_ports: List[dict]
    alerts_by_type: List[dict]
    alerts_by_severity: List[dict]