import app
from fastapi import FastAPI
from app.route.transaction_routes import  transaction_routes

app = FastAPI()

app.include_router(transaction_routes)