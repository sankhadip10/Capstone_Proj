FROM python:3.10

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# System packages - UPDATED: Added packages for image processing and testing
RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    gcc \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    tk-dev \
    tcl-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements - UPDATED: Install additional packages
COPY requirements.txt requirements-dev.txt ./

# Install dependencies - UPDATED: Install all packages including dev dependencies
RUN pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# NEW: Install additional packages for Docker environment
RUN pip install \
    pytest-xvfb \
    pytest-cov \
    razorpay

# Copy app code
COPY . /app/

# NEW: Create media directory for file uploads
RUN mkdir -p /app/media/store/images

# NEW: Set proper permissions
RUN chmod +x wait-for-it.sh docker-entrypoint.sh

# NEW: Create directory for logs
RUN mkdir -p /app/logs

# Collect static files - UPDATED: Handle errors gracefully
RUN python manage.py collectstatic --noinput || echo "Static files collection failed, continuing..."

# NEW: Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

EXPOSE 8000