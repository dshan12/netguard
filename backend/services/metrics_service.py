from sqlalchemy import select, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession
from models.packets import Packet
from models.alerts import Alert
from models.threat_actors import ThreatActor
from schemas.metrics import MetricsSummary, TimeSeriesData
from typing import List
from datetime import datetime, timedelta


class MetricsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary(self, minutes: int = 5) -> MetricsSummary:
        since = datetime.utcnow() - timedelta(minutes=minutes)

        packet_stats = await self.db.execute(
            select(
                func.count(Packet.id).label("total_packets"),
                func.sum(Packet.packet_size).label("total_bytes"),
            ).where(Packet.timestamp >= since)
        )
        ps = packet_stats.first()

        alert_stats = await self.db.execute(
            select(
                func.count(Alert.id).label("total_alerts"),
                func.sum(Alert.is_resolved).label("resolved"),
            ).where(Alert.timestamp >= since)
        )
        als = alert_stats.first()

        critical = await self.db.execute(
            select(func.count(Alert.id)).where(
                and_(Alert.timestamp >= since, Alert.severity == "Critical")
            )
        )
        high = await self.db.execute(
            select(func.count(Alert.id)).where(
                and_(Alert.timestamp >= since, Alert.severity == "High")
            )
        )
        medium = await self.db.execute(
            select(func.count(Alert.id)).where(
                and_(Alert.timestamp >= since, Alert.severity == "Medium")
            )
        )
        low = await self.db.execute(
            select(func.count(Alert.id)).where(
                and_(Alert.timestamp >= since, Alert.severity == "Low")
            )
        )

        active_threats = await self.db.execute(
            select(func.count(ThreatActor.id)).where(ThreatActor.threat_score > 50)
        )

        top_protocols = await self.db.execute(
            select(Packet.protocol, func.count(Packet.id).label("count"))
            .where(Packet.timestamp >= since)
            .group_by(Packet.protocol)
            .order_by(desc("count"))
            .limit(10)
        )

        top_src_ips = await self.db.execute(
            select(Packet.src_ip, func.count(Packet.id).label("count"))
            .where(Packet.timestamp >= since)
            .group_by(Packet.src_ip)
            .order_by(desc("count"))
            .limit(10)
        )

        top_dst_ports = await self.db.execute(
            select(Packet.dst_port, func.count(Packet.id).label("count"))
            .where(Packet.timestamp >= since, Packet.dst_port.isnot(None))
            .group_by(Packet.dst_port)
            .order_by(desc("count"))
            .limit(10)
        )

        alerts_by_type = await self.db.execute(
            select(Alert.alert_type, func.count(Alert.id).label("count"))
            .where(Alert.timestamp >= since)
            .group_by(Alert.alert_type)
            .order_by(desc("count"))
        )

        alerts_by_severity = await self.db.execute(
            select(Alert.severity, func.count(Alert.id).label("count"))
            .where(Alert.timestamp >= since)
            .group_by(Alert.severity)
        )

        total_packets = ps.total_packets or 0
        total_bytes = ps.total_bytes or 0

        return MetricsSummary(
            total_packets=total_packets,
            total_alerts=als.total_alerts or 0,
            active_threats=active_threats.scalar() or 0,
            critical_alerts=critical.scalar() or 0,
            high_alerts=high.scalar() or 0,
            medium_alerts=medium.scalar() or 0,
            low_alerts=low.scalar() or 0,
            packets_per_second=total_packets / max(1, minutes * 60),
            bytes_per_second=total_bytes / max(1, minutes * 60),
            top_protocols=[{"protocol": p.protocol, "count": p.count} for p in top_protocols],
            top_source_ips=[{"ip": str(p.src_ip), "count": p.count} for p in top_src_ips],
            top_destination_ports=[{"port": p.dst_port, "count": p.count} for p in top_dst_ports],
            alerts_by_type=[{"type": a.alert_type, "count": a.count} for a in alerts_by_type],
            alerts_by_severity=[{"severity": a.severity, "count": a.count} for a in alerts_by_severity],
        )

    async def get_packets_timeseries(self, minutes: int = 60, interval_seconds: int = 60) -> List[TimeSeriesData]:
        since = datetime.utcnow() - timedelta(minutes=minutes)
        result = await self.db.execute(
            text(f"""
                SELECT 
                    date_trunc('second', timestamp) + 
                    (extract(epoch from timestamp)::{int} / {interval_seconds}) * {interval_seconds} * interval '1 second' as bucket,
                    count(*) as value
                FROM packets
                WHERE timestamp >= :since
                GROUP BY bucket
                ORDER BY bucket
            """),
            {"since": since},
        )
        return [
            TimeSeriesData(timestamp=row.bucket, value=row.value)
            for row in result.all()
        ]

    async def get_alerts_timeseries(self, minutes: int = 60, interval_seconds: int = 60) -> List[TimeSeriesData]:
        since = datetime.utcnow() - timedelta(minutes=minutes)
        result = await self.db.execute(
            text(f"""
                SELECT 
                    date_trunc('second', timestamp) + 
                    (extract(epoch from timestamp)::{int} / {interval_seconds}) * {interval_seconds} * interval '1 second' as bucket,
                    count(*) as value,
                    severity as label
                FROM alerts
                WHERE timestamp >= :since
                GROUP BY bucket, severity
                ORDER BY bucket
            """),
            {"since": since},
        )
        return [
            TimeSeriesData(timestamp=row.bucket, value=row.value, label=row.label)
            for row in result.all()
        ]