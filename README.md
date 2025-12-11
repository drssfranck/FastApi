---
title: Financial Transactions API
emoji: 💳
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "2.0.0"
app_file: app.py
pinned: false
---

💳 Financial Transactions API
API REST avec FastAPI pour analyser les transactions financières et détecter les fraudes. Dataset de 1.26 GB téléchargé automatiquement depuis Kaggle.

🚀 Démarrage ultra-rapide
Prérequis
- Docker installé
- C'est tout ! Aucun compte Kaggle nécessaire

Installation en 2 commandes
```bash
# 1. Cloner le repository
git clone https://github.com/drssfranck/FastApi.git
cd financial-transactions-api

# 2. Lancer l'API
# Construire le container
docker build -t apibank .

# Executer la commande
docker run -p 8000:8000 apibank
