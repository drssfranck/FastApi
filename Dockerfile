FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY kaggle.json /root/.config/kaggle/kaggle.json
RUN chmod 600 /root/.config/kaggle/kaggle.json

COPY ./app ./app

CMD ["sh", "-c", "python app/data/import_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]



