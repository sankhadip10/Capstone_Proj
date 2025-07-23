#!/bin/bash

echo "🐳 Setting up Docker development environment..."

# Build and start core services
docker-compose up -d mysql redis smtp4dev

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Build and start main application
docker-compose up -d web

# Start background services
docker-compose up -d celery celery-beat flower

echo "✅ Development environment ready!"
echo ""
echo "🌐 Services available at:"
echo "  - Django App: http://localhost:8000"
echo "  - Flower (Celery): http://localhost:5555"
echo "  - SMTP4Dev (Email): http://localhost:5000"
echo "  - Admin: http://localhost:8000/admin (admin/1122334455)"