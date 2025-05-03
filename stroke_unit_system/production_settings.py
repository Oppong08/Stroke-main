import os
from settings import *

# Security settings
DEBUG = True  # Temporarily set to True to get detailed error messages
# Read the Render external URL from env var, fallback allows local testing if needed
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
ALLOWED_HOSTS = []
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
# Add other hosts like localhost if necessary for health checks or local access
ALLOWED_HOSTS.extend(['localhost', '127.0.0.1']) 

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key-here')  # Replace with a secure key

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', ''),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use simple storage in DEBUG mode to see detailed errors
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add static files directory
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Add WhiteNoise middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise middleware right after SecurityMiddleware
] + MIDDLEWARE

# Security middleware settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '') 