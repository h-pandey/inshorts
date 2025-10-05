@echo off
REM Fix Docker build issues script for Windows

echo 🔧 Fixing Docker build issues...

REM Stop any running containers
echo 1. Stopping running containers...
docker-compose down

REM Remove any partial builds
echo 2. Cleaning up Docker build cache...
docker system prune -f
docker builder prune -f

REM Remove any existing images
echo 3. Removing existing images...
docker rmi inshorts-app 2>nul
docker rmi $(docker images -q --filter "dangling=true") 2>nul

REM Build with simple app (no pydantic)
echo 4. Building with simple app Dockerfile...
docker-compose build --no-cache

echo 5. Starting services...
docker-compose up -d

echo ✅ Docker build fix completed!
echo 📋 Check status with: docker-compose ps
echo 📋 View logs with: docker-compose logs -f app
