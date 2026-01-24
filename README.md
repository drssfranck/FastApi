# 💳 **Financial Transactions API**

API REST avec **FastAPI** pour analyser les transactions financières et détecter les fraudes. Ce projet inclut un **dataset de 1.26 GB** téléchargé automatiquement depuis **Kaggle**.

## 🚀 **Démarrage ultra-rapide**

### Prérequis

- Docker installé
- Aucun compte Kaggle nécessaire (le dataset est téléchargé automatiquement)

### Installation en 2 commandes

```bash
# 1. Cloner le repository
git clone https://github.com/drssfranck/FastApi.git
cd financial-transactions-api

# 2. Lancer l'API
# Construire le container
docker build -t apibank .

# Exécuter le container
docker run -p 8000:8000 apibank
