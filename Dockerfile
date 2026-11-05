FROM python:3.13-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

ENV PORT=5000
EXPOSE 5000

CMD ["sh", "-c", "waitress-serve --host=0.0.0.0 --port=${PORT:-5000} server:app"]
