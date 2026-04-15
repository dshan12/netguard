from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ThreatActorResponse(BaseModel):
    id: int
    ip: str
    first_seen: datetime
    last_seen: datetime
    total_packets: int
    total_alerts: int
    threat_score: float
    categories: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_blocked: int

    model_config = ConfigDict(from_attributes=True)