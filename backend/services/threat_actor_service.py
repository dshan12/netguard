from sqlalchemy import select, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.threat_actors import ThreatActor
from schemas.threat_actors import ThreatActorResponse
from typing import List, Optional
from datetime import datetime, timedelta


class ThreatActorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, ip: str) -> ThreatActor:
        result = await self.db.execute(select(ThreatActor).where(ThreatActor.ip == ip))
        actor = result.scalar_one_or_none()
        if not actor:
            actor = ThreatActor(ip=ip)
            self.db.add(actor)
            await self.db.commit()
            await self.db.refresh(actor)
        return actor

    async def update_activity(self, ip: str, packet_count: int = 1, alert_count: int = 0, threat_score_delta: float = 0.0, category: str = None) -> ThreatActor:
        actor = await self.get_or_create(ip)
        actor.total_packets += packet_count
        actor.total_alerts += alert_count
        actor.threat_score = max(0.0, min(100.0, actor.threat_score + threat_score_delta))
        actor.last_seen = datetime.utcnow()
        if category:
            categories = set(actor.categories.split(",")) if actor.categories else set()
            categories.add(category)
            actor.categories = ",".join(categories)
        await self.db.commit()
        await self.db.refresh(actor)
        return actor

    async def get_top_threats(self, limit: int = 50) -> List[ThreatActor]:
        result = await self.db.execute(
            select(ThreatActor)
            .where(ThreatActor.threat_score > 0)
            .order_by(desc(ThreatActor.threat_score))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent(self, limit: int = 50) -> List[ThreatActor]:
        result = await self.db.execute(
            select(ThreatActor)
            .order_by(desc(ThreatActor.last_seen))
            .limit(limit)
        )
        return result.scalars().all()

    async def update_geo(self, ip: str, country: str, city: str, lat: float, lon: float) -> ThreatActor:
        actor = await self.get_or_create(ip)
        actor.country = country
        actor.city = city
        actor.latitude = lat
        actor.longitude = lon
        await self.db.commit()
        await self.db.refresh(actor)
        return actor