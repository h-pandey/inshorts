#!/bin/bash

# Fix Docker build issues script

echo "🔧 Fixing Docker build issues..."

# Stop any running containers
echo "1. Stopping running containers..."
docker-compose down

# Remove any partial builds
echo "2. Cleaning up Docker build cache..."
docker system prune -f
docker builder prune -f

# Remove any existing images
echo "3. Removing existing images..."
docker rmi inshorts-app 2>/dev/null || true
docker rmi $(docker images -q --filter "dangling=true") 2>/dev/null || true

# Build with minimal requirements
echo "4. Building with optimized Dockerfile..."
docker-compose build --no-cache

echo "5. Starting services..."
docker-compose up -d

echo "✅ Docker build fix completed!"
echo "📋 Check status with: docker-compose ps"
echo "📋 View logs with: docker-compose logs -f app"
