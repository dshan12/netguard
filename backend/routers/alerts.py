from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.alert_service import AlertService
from schemas.alerts import AlertResponse
from typing import List

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    severity: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = AlertService(db)
    if severity:
        return await service.get_by_severity(severity, limit=limit)
    return await service.get_recent(limit=limit, offset=offset)


@router.get("/unresolved", response_model=List[AlertResponse])
async def get_unresolved_alerts(
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db),
):
    service = AlertService(db)
    return await service.get_unresolved(limit=limit)


@router.get("/stats")
async def get_alert_stats(
    minutes: int = Query(60, ge=1, le=1440),
    db: AsyncSession = Depends(get_db),
):
    service = AlertService(db)
    return await service.get_stats(minutes=minutes)


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = AlertService(db)
    alert = await service.mark_resolved(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert resolved", "alert_id": alert_id}