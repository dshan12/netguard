from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.metrics_service import MetricsService
from schemas.metrics import MetricsSummary, TimeSeriesData
from typing import List

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    minutes: int = Query(5, ge=1, le=1440),
    db: AsyncSession = Depends(get_db),
):
    service = MetricsService(db)
    return await service.get_summary(minutes=minutes)


@router.get("/packets/timeseries", response_model=List[TimeSeriesData])
async def get_packets_timeseries(
    minutes: int = Query(60, ge=1, le=1440),
    interval: int = Query(60, ge=10, le=3600),
    db: AsyncSession = Depends(get_db),
):
    service = MetricsService(db)
    return await service.get_packets_timeseries(minutes=minutes, interval_seconds=interval)


@router.get("/alerts/timeseries", response_model=List[TimeSeriesData])
async def get_alerts_timeseries(
    minutes: int = Query(60, ge=1, le=1440),
    interval: int = Query(60, ge=10, le=3600),
    db: AsyncSession = Depends(get_db),
):
    service = MetricsService(db)
    return await service.get_alerts_timeseries(minutes=minutes, interval_seconds=interval)