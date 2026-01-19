import app
from fastapi import FastAPI
from app.route.transaction_routes import  transaction_routes
from app.route.clients_routes import client_route
<<<<<<< HEAD
from app.route.administration_routes import administration_route
=======
from app.route.administration_routes import administration
>>>>>>> b80199e31acd8d5490212164384224f95c4f8d3d
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
<<<<<<< HEAD
app.include_router(administration_route)
=======
app.include_router(administration)
>>>>>>> b80199e31acd8d5490212164384224f95c4f8d3d
