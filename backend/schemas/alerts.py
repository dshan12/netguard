from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class AlertBase(BaseModel):
    alert_type: str
    severity: str
    src_ip: str
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    description: str
    details: Optional[str] = None
    rule_triggered: Optional[str] = None
    anomaly_score: Optional[int] = None


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: int
    timestamp: datetime
    is_resolved: int = 0

    model_config = ConfigDict(from_attributes=True)