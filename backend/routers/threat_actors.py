from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.threat_actor_service import ThreatActorService
from schemas.threat_actors import ThreatActorResponse
from typing import List

router = APIRouter(prefix="/api/threat-actors", tags=["threat-actors"])


@router.get("/", response_model=List[ThreatActorResponse])
async def get_threat_actors(
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    service = ThreatActorService(db)
    return await service.get_top_threats(limit=limit)


@router.get("/recent", response_model=List[ThreatActorResponse])
async def get_recent_threat_actors(
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    service = ThreatActorService(db)
    return await service.get_recent(limit=limit)