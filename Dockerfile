FROM python:3.10
WORKDIR /app

# Install netcat for health checks in entrypoint scripts
RUN apt-get update && apt-get install -y netcat-openbsd gettext && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY docker-entrypoint.sh .

RUN python -m pip install --upgrade pip && pip install -r requirements.txt
RUN chmod +x docker-entrypoint.sh

COPY . .

RUN chmod +777 -R /app

EXPOSE 8000

CMD ["/app/docker-entrypoint.sh"]
