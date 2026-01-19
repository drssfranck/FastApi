from fastapi import APIRouter

administration_route=APIRouter()

@administration_route.get("/api/system/health")
def system_health():
    return {"status": "ok", "uptime": "2h 15min", "dataset_loaded": True }

@administration_route.get("/api/system/metadata")
def system_metadata():
    return { "version": "1.0.0", "last_update": "2025-12-20T22:00:00Z" }