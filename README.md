💳 Financial Transactions API
API REST avec FastAPI pour analyser les transactions financières et détecter les fraudes. Dataset de 1.26 GB téléchargé automatiquement depuis Kaggle.
🚀 Démarrage ultra-rapide
Prérequis

Docker installés
C'est tout ! Aucun compte Kaggle nécessaire

Installation en 2 commandes
bash# 1. Cloner le repository
git clone https://github.com/drssfranck/FastApi.git
cd financial-transactions-api

# 2. Lancer l'API
# Construire le container
docker build -t apibank .


# Executer la commande 
docker run -p 8000:8000 apibank

C'est tout ! ✨
Au premier lancement, le dataset sera automatiquement téléchargé (~1.26 GB). Cela prend 5-10 minutes selon ta connexion.
Accéder à l'API

API : http://localhost:8000
Documentation interactive : http://localhost:8000/docs
Documentation alternative : http://localhost:8000/redoc

📊 Endpoints disponibles

- Transactions
- Customers 
- Card






