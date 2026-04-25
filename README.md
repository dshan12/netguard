<div align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" alt="Python 3.12">
  <img src="https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react" alt="React 18">
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql" alt="PostgreSQL 16">
  <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/scikit--learn-1.4-F7931E?logo=scikit-learn" alt="scikit-learn">
  <br>
  <strong>Real-Time Network Attack Detection Platform</strong>
</div>

---

NetGuard captures live network traffic, detects malicious behavior through a hybrid signature + machine learning engine, and surfaces everything on a real-time dashboard — think CrowdStrike or Splunk, containerized and self-hosted.

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Packet     │───▶│  Redis       │───▶│  Detection   │───▶│  PostgreSQL  │
│  Sniffer    │    │  (Stream)    │    │  Engines     │    │              │
│  /Traffic   │    │              │    │  (Rules +    │    │              │
│  Simulator  │    │              │    │   ML)        │    │              │
└─────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                                  │
                                                    ┌─────────────▼────────┐
                                                    │  FastAPI Backend     │
                                                    │  (REST + WebSocket)  │
                                                    └───────────┬──────────┘
                                                                │
                                                    ┌───────────▼──────────┐
                                                    │  React Dashboard     │
                                                    │  (Live Map, Alerts,  │
                                                    │   ML Insights, Geo)  │
                                                    └──────────────────────┘
```

## Features

### Data Collection
- **Live packet capture** via Scapy on any network interface
- **Traffic simulator** generates realistic benign + attack traffic for demo/testing
- **Auto-fallback**: tries live capture, falls back to simulation if permissions are insufficient

### Detection Engine (5 Rules)
| Attack Type | Detection Method | Sliding Window |
|---|---|---|
| Port Scan | >20 unique dst ports per source IP | 10s |
| DDoS | >50 packets/sec to a single dst IP | 5s |
| Brute Force | >30 auth-port attempts per flow | 60s |
| Beaconing | Connection interval std dev < 0.5s over 3+ intervals | 300s |
| Data Exfiltration | >10KB outbound burst or >1400B packets | 60s |

### Machine Learning Ensemble (3 Models)
| Model | Type | Role |
|---|---|---|
| Isolation Forest | Unsupervised | Detects global outliers via recursive partitioning |
| Autoencoder (MLP) | Deep Learning | Flags IPs with high reconstruction error (bottleneck 9→3→9) |
| K-Means Clustering | Unsupervised | Identifies IPs far from behavior cluster centroids |

The ensemble combines all three (weights: 40% IF + 30% AE + 30% clustering) for robust detection. Alerts track which models agreed.

### Dashboard
- **Live Network Map** — Canvas particle animation showing IP-to-IP flows in real time
- **Alert Timeline** — Scrollable, color-coded by severity (Critical/High/Medium/Low)
- **Geographic Map** — World map plotting threat source locations with pulsing markers
- **Threat Metrics** — Live packet throughput, alert counts, active threats
- **ML Insights** — Anomaly score distributions, feature importance, model status

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy (async), Pydantic |
| Database | PostgreSQL 16 |
| Cache / Stream | Redis 7 |
| ML | scikit-learn (Isolation Forest, MLPRegressor, KMeans), pandas, numpy |
| Packet Capture | Scapy |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Recharts |
| Infrastructure | Docker Compose, uv (Python package manager) |

## Quick Start

```bash
# Clone
git clone https://github.com/dshan12/netguard.git
cd netguard

# Copy environment
cp .env.example .env

# Start all services
docker compose up -d

# Access the dashboard
open http://localhost:3000

# Check backend API
curl http://localhost:8000/health
```

The traffic simulator starts automatically — you'll see alerts within seconds.

## Services

| Service | Port | Description |
|---|---|---|
| `frontend` | 3000 | React dashboard |
| `backend` | 8000 | FastAPI REST + WebSocket |
| `backend-worker` | — | Redis → PostgreSQL consumer |
| `sniffer` | — | Packet capture + rules engine |
| `ml-worker` | — | ML ensemble training + inference |
| `postgres` | 5432 | Persistent storage |
| `redis` | 6379 | Message broker / stream |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/packets/` | Recent packets (paginated) |
| GET | `/api/packets/suspicious` | Flagged packets |
| GET | `/api/alerts/` | Alerts (filterable by severity) |
| GET | `/api/alerts/stats` | Alert statistics |
| POST | `/api/alerts/{id}/resolve` | Resolve an alert |
| GET | `/api/threat-actors/` | Top threat actors |
| GET | `/api/metrics/summary` | Dashboard metrics |
| GET | `/api/geo/sources` | Geo-located threat sources |
| WS | `/ws/live` | Real-time packet + alert stream |

Full OpenAPI docs at `http://localhost:8000/docs`.

## Project Structure

```
netguard/
├── docker-compose.yml       # Orchestrates all 7 services
├── .env.example             # Environment template
├── backend/                 # FastAPI application
│   ├── main.py              # App entry + router registration
│   ├── worker.py            # Redis queue consumer
│   ├── models/              # SQLAlchemy ORM models
│   ├── routers/             # API endpoint definitions
│   ├── schemas/             # Pydantic request/response models
│   └── services/            # Business logic layer
├── sniffer/                 # Packet capture and detection
│   ├── sniffer.py           # Scapy-based capture + simulation dispatch
│   ├── generator.py         # Traffic simulator (6 traffic types)
│   └── rules_engine.py      # 5 signature-based detection rules
├── ml-worker/               # Machine learning pipeline
│   ├── model.py             # Training + inference loop
│   ├── ml_ensemble.py       # Ensemble detector (3 models)
│   └── features.py          # Per-IP feature extraction (9 features)
└── frontend/                # React dashboard
    ├── src/
    │   ├── App.tsx          # 4-tab layout (Dashboard, Alerts, Map, ML)
    │   ├── components/      # NetworkMap, AlertTimeline, MetricsGrid, GeoMap
    │   ├── pages/           # AlertsPage, MapPage, MLInsightsPage
    │   └── hooks/           # useWebSocket (live data streaming)
    └── ...config files
```

## Development

```bash
# Backend
cd backend && uv sync && uv run uvicorn main:app --reload

# Sniffer (standalone simulation)
cd sniffer && SIMULATION_MODE=always uv run python sniffer.py

# ML Worker
cd ml-worker && uv run python model.py

# Frontend
cd frontend && bun install && bun run dev
```
