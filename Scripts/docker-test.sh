#!/bin/bash

echo "🧪 Running tests in Docker..."

# Start required services
docker-compose up -d mysql redis

# Wait for services
sleep 5

# Run tests
docker-compose --profile testing run --rm tests

# Cleanup
docker-compose --profile testing down