from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Index, Float
from sqlalchemy.dialects.postgresql import INET
from database import Base
from datetime import datetime


class ThreatActor(Base):
    __tablename__ = "threat_actors"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ip = Column(INET, unique=True, nullable=False, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    total_packets = Column(BigInteger, default=0, nullable=False)
    total_alerts = Column(Integer, default=0, nullable=False)
    threat_score = Column(Float, default=0.0, nullable=False)
    categories = Column(String(500), nullable=True)
    country = Column(String(2), nullable=True)
    city = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_blocked = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("ix_threat_actors_score", "threat_score"),
        Index("ix_threat_actors_last_seen", "last_seen"),
    )