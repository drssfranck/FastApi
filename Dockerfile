FROM python:3.11-slim

WORKDIR /app

# Copier le fichier requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Créer le répertoire pour la configuration Kaggle
RUN mkdir -p /root/.kaggle

# Copier l'application
COPY ./app ./app

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["sh", "-c", "python app/data/import_data.py && uvicorn app.main:app --host 0.0.0.0 --port 7860"]