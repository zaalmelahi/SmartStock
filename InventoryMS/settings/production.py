import os
from .base import *

# 1. CRITICAL Security Settings
# Use environment variables for sensitive information
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# DEBUG must be False in production
DEBUG = False

# Define allowed hosts (e.g., ['.yourdomain.com', 'your-ip-address'])
ALLOWED_HOSTS = ['*']

# Secure Database credentials
# Expecting DATABASE_URL or individual params. 
# For production, PostgreSQL is highly recommended.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# 2. HTTPS/SSL Settings
# Ensure all connections are redirected to HTTPS
SECURE_SSL_REDIRECT = True
# Needed if behind a proxy like Nginx or Load Balancer
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Ensure cookies are only sent over HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 3. HSTS Configuration
# Strict-Transport-Security header
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 4. Cookie Security
# Prevent JavaScript from accessing session cookies
SESSION_COOKIE_HTTPONLY = True
# Prevent CSRF tokens from being sent in cross-site requests
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# 5. Content Security
# Prevent clickjacking
X_FRAME_OPTIONS = 'DENY'
# Prevent content type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True
# Enable browser XSS filtering
SECURE_BROWSER_XSS_FILTER = True

# Static and Media handling for production
# Usually served by Nginx or WhiteNoise
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
