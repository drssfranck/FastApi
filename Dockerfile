# ---- Stage 1: generate requirements.txt automatically ----
FROM python:3.13.9 AS builder

WORKDIR /app
COPY ./app ./app

# Installer seulement ton projet (si setup.py ou pyproject.toml)
# Sinon installer manuellement ce dont tu as besoin :
RUN pip install fastapi uvicorn kaggle pandas numpy

RUN pip freeze > requirements.txt


# ---- Stage 2: final image ----
FROM python:3.13.9

WORKDIR /app

COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY kaggle.json /root/.config/kaggle/kaggle.json
RUN chmod 600 /root/.config/kaggle/kaggle.json

COPY ./app ./app

CMD ["sh", "-c", "python app/data/import_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]


