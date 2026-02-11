FROM python:3.11-slim

# Définir des variables d'environnement pour éviter la génération de fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copier le fichier requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirem ents.txt

# Créer l'utilisateur non-root pour exécuter l'application
RUN useradd -m appuser
USER appuser

# Copier l'application
COPY ./app ./app

# Exposer le port
EXPOSE 8000

# Ajouter la gestion des variables d'environnement pour Kaggle
# Utiliser des variables d'environnement pour éviter d'inclure le fichier kaggle.json dans l'image
ENV KAGGLE_USERNAME=${KAGGLE_USERNAME}
ENV KAGGLE_KEY=${KAGGLE_KEY}

# Commande de démarrage pour lancer l'importation des données une seule fois et démarrer FastAPI
CMD ["sh", "-c", "python app/data/import_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
