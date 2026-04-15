from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.threat_actors import ThreatActor
from typing import List

router = APIRouter(prefix="/api/geo", tags=["geo"])


@router.get("/sources")
async def get_geo_sources(db: AsyncSession = Depends(get_db)):
    query = select(
        ThreatActor.ip,
        ThreatActor.latitude,
        ThreatActor.longitude,
        ThreatActor.threat_score,
        ThreatActor.country,
        ThreatActor.city,
        ThreatActor.total_alerts,
        ThreatActor.categories,
    ).where(
        ThreatActor.latitude.isnot(None),
        ThreatActor.longitude.isnot(None),
        ThreatActor.threat_score > 0,
    )
    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "ip": str(row.ip),
            "latitude": row.latitude,
            "longitude": row.longitude,
            "threat_score": row.threat_score,
            "country": row.country,
            "city": row.city,
            "total_alerts": row.total_alerts,
            "categories": row.categories,
        }
        for row in rows
    ]
