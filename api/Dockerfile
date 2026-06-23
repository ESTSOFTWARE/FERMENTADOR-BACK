FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Railway inyecta $PORT; en local usa 8000 por defecto.
# --proxy-headers + --forwarded-allow-ips: respeta X-Forwarded-Proto/Host del
# proxy de Railway, para que los redirects (ej. trailing slash) usen https y el
# dominio público, no la URL interna http (evita el Mixed Content en el front).
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]