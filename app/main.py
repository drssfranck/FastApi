import app
from fastapi import FastAPI
from app.route.transaction_routes import  transaction_routes
from app.route.clients_routes import client_route
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transaction_routes)
app.include_router(client_route)