from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Index
from sqlalchemy.dialects.postgresql import INET
from database import Base
from datetime import datetime


class Packet(Base):
    __tablename__ = "packets"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    src_ip = Column(INET, nullable=False, index=True)
    dst_ip = Column(INET, nullable=False, index=True)
    src_port = Column(Integer, nullable=True)
    dst_port = Column(Integer, nullable=True, index=True)
    protocol = Column(String(10), nullable=False)
    packet_size = Column(Integer, nullable=False)
    tcp_flags = Column(String(20), nullable=True)
    payload_size = Column(Integer, nullable=True)
    direction = Column(String(10), nullable=True)
    is_suspicious = Column(Integer, default=0, nullable=False)
    anomaly_score = Column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_packets_src_dst_time", "src_ip", "dst_ip", "timestamp"),
        Index("ix_packets_suspicious_time", "is_suspicious", "timestamp"),
    )