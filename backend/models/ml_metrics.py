from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Index, Float, Text
from sqlalchemy.dialects.postgresql import INET
from database import Base
from datetime import datetime


class MLMetric(Base):
    __tablename__ = "ml_metrics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip = Column(INET, nullable=False, index=True)
    feature_vector = Column(Text, nullable=True)
    anomaly_score = Column(Float, nullable=False, index=True)
    is_anomalous = Column(Integer, default=0, nullable=False)
    model_version = Column(String(50), nullable=True)
    features = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_ml_metrics_ip_time", "ip", "timestamp"),
        Index("ix_ml_metrics_anomaly_time", "is_anomalous", "timestamp"),
    )