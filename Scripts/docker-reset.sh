#!/bin/bash

echo "🗑️ Resetting Docker environment..."

# Stop all services
docker-compose down

# Remove volumes (WARNING: This deletes all data!)
read -p "⚠️  This will delete all data. Continue? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down -v
    docker system prune -f
    echo "✅ Environment reset complete"
else
    echo "❌ Reset cancelled"
fi