from fastapi import APIRouter
from datetime import datetime, timezone
from app.data.load_data import is_dataset_loaded
from build_info import VERSION, BUILD_DATE



START_TIME = datetime.now(timezone.utc)


def get_uptime() -> str:
    delta = datetime.now(timezone.utc) - START_TIME
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}min"


def health_status():
    return {
        "status": "ok",
        "uptime": get_uptime(),
        "dataset_loaded": is_dataset_loaded()
    }

administration = APIRouter(prefix="/api/system", tags=["System"])


#app/route/administration_routes.py 20
@administration.get("/metadata")
def metadata():
    return {"version": VERSION, "last_update": BUILD_DATE}


#app/route/administration_routes.py 19
@administration.get("/health")
def health():
    return health_status()
