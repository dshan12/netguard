from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.alerts import Alert
from schemas.alerts import AlertCreate
from typing import List, Optional
from datetime import datetime, timedelta


class AlertService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, alert: AlertCreate) -> Alert:
        db_alert = Alert(**alert.model_dump())
        self.db.add(db_alert)
        await self.db.commit()
        await self.db.refresh(db_alert)
        return db_alert

    async def create_batch(self, alerts: List[AlertCreate]) -> List[Alert]:
        db_alerts = [Alert(**a.model_dump()) for a in alerts]
        self.db.add_all(db_alerts)
        await self.db.commit()
        for a in db_alerts:
            await self.db.refresh(a)
        return db_alerts

    async def get_recent(self, limit: int = 100, offset: int = 0) -> List[Alert]:
        result = await self.db.execute(
            select(Alert).order_by(desc(Alert.timestamp)).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_by_severity(self, severity: str, limit: int = 100) -> List[Alert]:
        result = await self.db.execute(
            select(Alert)
            .where(Alert.severity == severity)
            .order_by(desc(Alert.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_unresolved(self, limit: int = 100) -> List[Alert]:
        result = await self.db.execute(
            select(Alert)
            .where(Alert.is_resolved == 0)
            .order_by(desc(Alert.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_stats(self, minutes: int = 60) -> dict:
        since = datetime.utcnow() - timedelta(minutes=minutes)
        result = await self.db.execute(
            select(
                Alert.severity,
                func.count(Alert.id).label("count"),
            )
            .where(Alert.timestamp >= since)
            .group_by(Alert.severity)
        )
        severity_counts = {row.severity: row.count for row in result.all()}

        type_result = await self.db.execute(
            select(
                Alert.alert_type,
                func.count(Alert.id).label("count"),
            )
            .where(Alert.timestamp >= since)
            .group_by(Alert.alert_type)
        )
        type_counts = {row.alert_type: row.count for row in type_result.all()}

        return {
            "by_severity": severity_counts,
            "by_type": type_counts,
            "total": sum(severity_counts.values()),
        }

    async def mark_resolved(self, alert_id: int) -> Optional[Alert]:
        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        if alert:
            alert.is_resolved = 1
            await self.db.commit()
            await self.db.refresh(alert)
        return alert