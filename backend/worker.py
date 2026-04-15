import asyncio
import json
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session_maker
from models.packets import Packet
from models.alerts import Alert
from config import get_settings

settings = get_settings()

async def process_redis_queues():
    while True:
        try:
            redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            await redis_client.ping()
            print("Redis connection established.")
            break
        except Exception as e:
            print(f"Redis connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

    print("Background worker started. Processing queues...")
    
    while True:
        try:
            # Process packets batch
            packets_to_save = []
            for _ in range(100): # Process up to 100 at a time
                data = await redis_client.rpop("pending_packets")
                if not data:
                    break
                packets_to_save.append(json.loads(data))
            
            if packets_to_save:
                async with async_session_maker() as session:
                    db_packets = [Packet(**p) for p in packets_to_save]
                    session.add_all(db_packets)
                    await session.commit()
                # print(f"Saved {len(packets_to_save)} packets to database")

            # Process alerts batch
            alerts_to_save = []
            for _ in range(10):
                data = await redis_client.rpop("pending_alerts")
                if not data:
                    break
                alerts_to_save.append(json.loads(data))
            
            if alerts_to_save:
                async with async_session_maker() as session:
                    db_alerts = [Alert(**a) for a in alerts_to_save]
                    session.add_all(db_alerts)
                    await session.commit()
                print(f"Saved {len(alerts_to_save)} alerts to database")

            await asyncio.sleep(1)
        except Exception as e:
            print(f"Worker error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(process_redis_queues())
