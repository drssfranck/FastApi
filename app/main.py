from fastapi import FastAPI
from app.route.transaction_routes import transaction_routes
from app.route.clients_routes import client_route
from app.route.administration_routes import administration
from fastapi.middleware.cors import CORSMiddleware
# Importez votre logique de chargement ici
from app.data.load_data import load_all_datasets 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# On définit ce qui doit se passer au lancement du serveur
@app.on_event("startup")
async def startup_event():
    try:
        # Appelez ici votre fonction qui charge les CSV
        load_all_datasets()
        print("Datasets chargés avec succès.")
    except Exception as e:
        # Sur GitHub, cela affichera l'erreur mais ne fera pas crash le test
        print(f"Avertissement : Erreur lors du chargement des données (attendu en CI) : {e}")

app.include_router(transaction_routes)
app.include_router(client_route)
app.include_router(administration)