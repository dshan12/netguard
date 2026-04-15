from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import get_settings
from database import init_db
from routers import packets, alerts, threat_actors, metrics, websocket, geo

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Security Analytics API",
    description="Real-time Attack Detection Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(packets.router)
app.include_router(alerts.router)
app.include_router(threat_actors.router)
app.include_router(metrics.router)
app.include_router(websocket.router)
app.include_router(geo.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Security Analytics API", "version": "0.1.0"}