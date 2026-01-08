# Docker Compose Usage Guide

This project uses Docker Compose with profiles to manage different service configurations.

## Available Profiles

### 1. Sales & Inventory Management (Profile: `sales`)
The main application with database.

**Services:**
- `web`: Django application server
- `db`: PostgreSQL database

**Start the sales profile:**
```bash
docker compose --profile sales up -d
```

**Access:**
- Application: http://localhost:8000
- Database: localhost:5435 (external port)

### 2. Database Admin (Profile: `admin`)
PgAdmin for database management (optional).

**Services:**
- `pgadmin`: Database administration interface

**Start the admin profile:**
```bash
docker compose --profile admin up -d
```

**Access:**
- PgAdmin: http://localhost:5052

### 3. WPPConnect (Profile: `wppconnect`)
WhatsApp Web API service for messaging integration.

**Services:**
- `wppconnect`: WhatsApp connection server

**Start the wppconnect profile:**
```bash
docker compose --profile wppconnect up -d
```

**Access:**
- WPPConnect API: http://localhost:21465

## Running Multiple Profiles

You can run multiple profiles simultaneously:

```bash
# Run both sales and wppconnect
docker compose --profile sales --profile wppconnect up -d
```

## Common Commands

```bash
# Build images
docker compose build

# Start services (with profile)
docker compose --profile sales up -d

# Stop services
docker compose --profile sales down

# View logs
docker compose --profile sales logs -f web

# Restart a service
docker compose --profile sales restart web

# Run migrations
docker compose --profile sales exec web python manage.py migrate

# Create superuser
docker compose --profile sales exec web python manage.py createsuperuser

# Collect static files
docker compose --profile sales exec web python manage.py collectstatic --noinput
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:
- `DJANGO_ENV`: Set to `production` for Gunicorn, or `development` for Django dev server
- `DB_HOST`: Use `db` for Docker, `localhost` for local development
- `WEB_PORT`: Web application port (default: 8000)
- `WPPCONNECT_PORT`: WPPConnect API port (default: 21465)

## Production Deployment

For production, set these in `.env`:

```bash
DJANGO_ENV=production
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-secure-random-key
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Then start with:

```bash
docker compose --profile sales up -d
```

The application will automatically use Gunicorn in production mode.
