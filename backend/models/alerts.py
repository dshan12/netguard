from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, Index, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    src_ip = Column(INET, nullable=False, index=True)
    dst_ip = Column(INET, nullable=True, index=True)
    src_port = Column(Integer, nullable=True)
    dst_port = Column(Integer, nullable=True)
    protocol = Column(String(10), nullable=True)
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    rule_triggered = Column(String(100), nullable=True)
    anomaly_score = Column(Integer, nullable=True)
    is_resolved = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("ix_alerts_severity_time", "severity", "timestamp"),
        Index("ix_alerts_src_time", "src_ip", "timestamp"),
    )