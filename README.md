<div align="center">

# NetGuard

**Real-time network attack detection.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://docker.com)

Captures network traffic, detects attacks through rules + ML, and shows it all on a live dashboard. Containerized, self-hosted — think a miniature CrowdStrike/Splunk.

</div>

## Quick start

```bash
git clone https://github.com/dshan12/netguard.git && cd netguard
cp .env.example .env
docker compose up -d
# open http://localhost:3000
```

The traffic simulator starts automatically. You'll see alerts within seconds.

## How it works

Packets come in via Scapy (or the built-in simulator if live capture isn't available) and get published to Redis. Two things consume that stream in parallel:

1. **A rules engine** — 5 sliding-window detectors for the usual suspects: port scans, DDoS spikes, brute force attempts, beaconing, data exfiltration.
2. **An ML ensemble** — every few minutes it extracts per-IP flow features and runs three models (Isolation Forest, a bottleneck autoencoder, and K-Means clustering). The scores are weighted together. Alerts note which models agreed.

Both write to PostgreSQL. FastAPI serves REST endpoints and a WebSocket that pushes live packets and alerts to the React frontend.

```
Sniffer/Simulator → Redis → Rules Engine + ML Worker → PostgreSQL → FastAPI → React Dashboard
```

## Detection

| Attack | What it looks for |
|---|---|
| Port scan | >20 unique ports from one source in 10s |
| DDoS | >50 packets/sec to a single target |
| Brute force | >30 auth-port attempts in 60s |
| Beaconing | Regular connection intervals (std dev < 0.5s) |
| Exfiltration | Large outbound bursts or oversized packets |

## ML models

| Model | What it does |
|---|---|
| Isolation Forest | Flags IPs that look different from everyone else |
| Autoencoder (MLP) | Flags IPs that are hard to reconstruct from compressed features |
| K-Means | Flags IPs far from their cluster centroid |

Each IP gets three scores. The final verdict is 40% IF + 30% AE + 30% clustering.

## Dashboard

- **Live Network Map** — particles flying between IPs on a canvas
- **Alert Timeline** — scrollable, color-coded by severity
- **Geo Map** — threat sources plotted on a world map
- **ML Insights** — score distributions, model status, flagged IPs

## Tech

Backend: FastAPI + SQLAlchemy (async) + PostgreSQL + Redis  
ML: scikit-learn (Isolation Forest, MLPRegressor, KMeans) + pandas  
Capture: Scapy  
Frontend: React 18 + TypeScript + Vite + Tailwind + Recharts  
Infra: Docker Compose, uv

## API

| Endpoint | What it returns |
|---|---|
| `GET /health` | Health check |
| `GET /api/packets/` | Recent packets |
| `GET /api/alerts/` | Alerts (filter by severity) |
| `POST /api/alerts/{id}/resolve` | Resolve an alert |
| `GET /api/threat-actors/` | Top threats by score |
| `GET /api/metrics/summary` | Dashboard metrics |
| `GET /api/geo/sources` | Geo-located threats |
| `WS /ws/live` | Real-time stream |

Full docs at `localhost:8000/docs`.

## Running locally (no Docker)

You'll need PostgreSQL, Redis, Python 3.12+ (with uv), and Bun.

```bash
cd backend   && uv sync && uv run uvicorn main:app --reload     # :8000
cd sniffer   && SIMULATION_MODE=always uv run python sniffer.py # generates traffic
cd ml-worker && uv run python model.py                          # ML inference
cd frontend  && bun install && bun run dev                      # :3000
```

## Project layout

```
backend/       FastAPI app, models, routers, services
sniffer/       Scapy capture, traffic generator, rules engine
ml-worker/     Feature extraction, ensemble detector
frontend/      React dashboard (4 tabs)
```

## License

MIT
