from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from ipaddress import IPv4Address, IPv6Address


class PacketBase(BaseModel):
    src_ip: str
    dst_ip: str
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: str
    packet_size: int
    tcp_flags: Optional[str] = None
    payload_size: Optional[int] = None
    direction: Optional[str] = None
    is_suspicious: int = 0
    anomaly_score: Optional[int] = None


class PacketCreate(PacketBase):
    pass


class PacketResponse(PacketBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)