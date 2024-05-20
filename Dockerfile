FROM python:3.9-slim

WORKDIR /app

COPY . .
RUN pip install firebase-admin fastapi uvicorn

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
