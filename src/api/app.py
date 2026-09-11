from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(
    title="Privacy-Aware Security Monitoring System API",
    description="Initial API skeleton for security monitoring, detection, and privacy-aware data storage.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {
        "message": "Privacy-Aware Security Monitoring System API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "security-monitoring-api",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
