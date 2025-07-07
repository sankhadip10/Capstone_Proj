FROM python:3.10

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# System packages
RUN apt-get update && apt-get install -y \
    python3-dev default-libmysqlclient-dev gcc

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements
COPY requirements.txt requirements-dev.txt ./

# Control whether to install dev packages
# Install prod + dev dependencies
RUN pip install -r requirements.txt \
    && pip install -r requirements-dev.txt

# Copy app code
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000
