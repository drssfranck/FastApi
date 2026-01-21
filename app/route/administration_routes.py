from fastapi import APIRouter

administration_route = APIRouter()

@administration_route.get("/api/administration/health")
def health_check():
    """Route de vérification de la santé du serveur"""
    return {"status": "ok", "message": "API running"}
