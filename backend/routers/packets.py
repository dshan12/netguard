from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.packet_service import PacketService
from schemas.packets import PacketResponse
from typing import List

router = APIRouter(prefix="/api/packets", tags=["packets"])


@router.get("/", response_model=List[PacketResponse])
async def get_packets(
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    service = PacketService(db)
    return await service.get_recent(limit=limit, offset=offset)


@router.get("/suspicious", response_model=List[PacketResponse])
async def get_suspicious_packets(
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db),
):
    service = PacketService(db)
    return await service.get_suspicious(limit=limit)


@router.get("/ip/{ip}", response_model=List[PacketResponse])
async def get_packets_by_ip(
    ip: str,
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db),
):
    service = PacketService(db)
    return await service.get_by_ip(ip, limit=limit)