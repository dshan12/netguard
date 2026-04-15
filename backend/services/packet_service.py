from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.packets import Packet
from schemas.packets import PacketCreate
from typing import List, Optional
from datetime import datetime, timedelta


class PacketService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, packet: PacketCreate) -> Packet:
        db_packet = Packet(**packet.model_dump())
        self.db.add(db_packet)
        await self.db.commit()
        await self.db.refresh(db_packet)
        return db_packet

    async def create_batch(self, packets: List[PacketCreate]) -> List[Packet]:
        db_packets = [Packet(**p.model_dump()) for p in packets]
        self.db.add_all(db_packets)
        await self.db.commit()
        for p in db_packets:
            await self.db.refresh(p)
        return db_packets

    async def get_recent(self, limit: int = 100, offset: int = 0) -> List[Packet]:
        result = await self.db.execute(
            select(Packet).order_by(desc(Packet.timestamp)).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_suspicious(self, limit: int = 100) -> List[Packet]:
        result = await self.db.execute(
            select(Packet)
            .where(Packet.is_suspicious == 1)
            .order_by(desc(Packet.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_ip(self, ip: str, limit: int = 100) -> List[Packet]:
        result = await self.db.execute(
            select(Packet)
            .where((Packet.src_ip == ip) | (Packet.dst_ip == ip))
            .order_by(desc(Packet.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_stats(self, minutes: int = 5) -> dict:
        since = datetime.utcnow() - timedelta(minutes=minutes)
        result = await self.db.execute(
            select(
                func.count(Packet.id).label("count"),
                func.sum(Packet.packet_size).label("bytes"),
                func.count(Packet.id.distinct()).label("unique_ips"),
            ).where(Packet.timestamp >= since)
        )
        row = result.first()
        return {
            "count": row.count or 0,
            "bytes": row.bytes or 0,
            "unique_ips": row.unique_ips or 0,
        }