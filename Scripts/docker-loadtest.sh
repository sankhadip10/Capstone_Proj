#!/bin/bash

echo "⚡ Setting up load testing..."

# Start application
docker-compose up -d web mysql redis

# Wait for app to be ready
echo "⏳ Waiting for application..."
sleep 15

# Start Locust
echo "🚀 Starting Locust..."
docker-compose --profile loadtest up locust