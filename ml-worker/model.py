import asyncio
import pandas as pd
import numpy as np
import time
import json
import redis.asyncio as redis
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from pydantic_settings import BaseSettings
from features import extract_features
from ml_ensemble import EnsembleDetector, FeatureNormalizer

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://security_user:security_pass@postgres:5432/security_analytics"
    redis_url: str = "redis://redis:6379/0"
    model_update_interval: int = 300
    anomaly_threshold: float = 0.7

    model_config = {"protected_namespaces": ()}

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class AnomalyDetector:
    def __init__(self):
        self.normalizer = FeatureNormalizer()
        self.ensemble = EnsembleDetector(threshold=settings.anomaly_threshold)
        self.is_trained = False

    async def run(self):
        print("ML Anomaly Detector started...")

        # Initial Redis healthcheck
        try:
            redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            await redis_client.ping()
            await redis_client.aclose()
            print("Redis healthcheck: OK")
        except Exception as e:
            print(f"Redis healthcheck: FAILED ({e})")

        while True:
            try:
                await self.process_cycle()

                # Periodic Redis healthcheck
                try:
                    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
                    await redis_client.ping()
                    await redis_client.aclose()
                    print("Redis healthcheck: OK")
                except Exception as e:
                    print(f"Redis healthcheck: FAILED ({e})")
            except Exception as e:
                print(f"ML Error: {e}")
            await asyncio.sleep(60)

    async def process_cycle(self):
        # 1. Fetch recent packets (last 5 minutes)
        async with async_session() as session:
            query = text("SELECT id, src_ip, dst_ip, src_port, dst_port, protocol, packet_size FROM packets WHERE timestamp > NOW() - INTERVAL '5 minutes'")
            result = await session.execute(query)
            rows = result.all()
            
            if len(rows) < 100:
                print(f"Not enough data for ML yet ({len(rows)} packets)")
                return

            df = pd.DataFrame(rows, columns=['id', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol', 'packet_size'])
            
            # 2. Extract features
            features = extract_features(df)
            if features.empty:
                return

            # 3. Normalize features
            X_norm = self.normalizer.fit_transform(features)
            
            # 4. Train ensemble
            self.ensemble.fit(X_norm)
            self.is_trained = True
            print(f"Ensemble trained on {len(features)} IP profiles, status: {self.ensemble.get_model_status()}")
            
            # 5. Predict on all profiles
            results = self.ensemble.predict(X_norm)
            
            # 6. Generate alerts for anomalous IPs
            for i, (src_ip, row) in enumerate(features.iterrows()):
                is_score = float(results['isolation_forest_score'][i])
                ae_score = float(results['autoencoder_score'][i])
                cl_score = float(results['clustering_score'][i])
                ensemble_score = float(results['ensemble_score'][i])
                is_anomaly = results['is_anomaly'][i]
                
                # Build model agreement info
                agreeing_models = []
                if is_score > settings.anomaly_threshold:
                    agreeing_models.append("IsolationForest")
                if ae_score > settings.anomaly_threshold:
                    agreeing_models.append("Autoencoder")
                if cl_score > settings.anomaly_threshold:
                    agreeing_models.append("Clustering")
                
                print(f"IP {src_ip} | IS={is_score:.2f} AE={ae_score:.2f} CL={cl_score:.2f} Ensemble={ensemble_score:.2f} | Models: {agreeing_models}")
                
                if is_anomaly:
                    models_str = "+".join(agreeing_models) if agreeing_models else "Ensemble"
                    print(f"ML Anomaly Alert: {src_ip} with ensemble score {ensemble_score:.2f} ({models_str})")
                    alert = {
                        "alert_type": "ML Anomaly Detected",
                        "severity": "Medium" if ensemble_score < 0.9 else "High",
                        "src_ip": src_ip,
                        "description": f"Anomaly detected for IP {src_ip} (Ensemble Score: {ensemble_score:.2f}, Models: {models_str})",
                        "rule_triggered": f"ML_ENSEMBLE_{models_str.upper()}",
                        "anomaly_score": int(ensemble_score * 100),
                        "isolation_forest_score": int(is_score * 100),
                        "autoencoder_score": int(ae_score * 100),
                        "clustering_score": int(cl_score * 100),
                    }
                    
if __name__ == "__main__":
    detector = AnomalyDetector()
    asyncio.run(detector.run())
