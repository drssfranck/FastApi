from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.route.main import root_routes
from app.route.transaction_routes import router
from app.route.clients_routes import client_route
from app.route.administration_routes import administration_route
from app.route.statistiques_routes import stat_router
from app.route.fraude_routes import fraud_routes

app = FastAPI(
    title="Fraud Detection API",
    description="API de démonstration pour l’analyse "
                "de transactions et la détection de fraude.",
    version="1.0.0",
)


# ------------------------------------------------------------------
# Middleware CORS
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
app.include_router(root_routes)
app.include_router(router)
app.include_router(client_route)
app.include_router(administration_route)
app.include_router(fraud_routes)
app.include_router(stat_router)
