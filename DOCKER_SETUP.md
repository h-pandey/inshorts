# Docker Setup Guide

This guide explains how to set up and run the Contextual News API using Docker and Docker Compose.

## 🐳 Prerequisites

### Required Software
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (included with Docker Desktop)
- **Git** (for cloning the repository)

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk Space**: At least 2GB free space
- **CPU**: 2+ cores recommended

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd contextual-news-api

# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# At minimum, set: OPENAI_API_KEY=your_key_here
```

### 2. Start Services

**Using the setup script (Recommended):**

```bash
# Linux/Mac
./scripts/docker-setup.sh start

# Windows
scripts\docker-setup.bat start

# Or manually
docker-compose up --build -d
```

### 3. Verify Setup

```bash
# Check service health
./scripts/docker-setup.sh health
# or
scripts\docker-setup.bat health

# View service URLs
./scripts/docker-setup.sh urls
# or
scripts\docker-setup.bat urls
```

## 📋 Services Overview

| Service | Port | Description | Admin UI |
|---------|------|-------------|----------|
| **app** | 8000 | FastAPI Application | - |
| **mongodb** | 27017 | MongoDB Database | http://localhost:8081 |
| **redis** | 6379 | Redis Cache | http://localhost:8082 |
| **nginx** | 80/443 | Reverse Proxy (optional) | - |

### Service URLs
- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **MongoDB Admin**: http://localhost:8081 (admin/admin123)
- **Redis Admin**: http://localhost:8082 (admin/admin123)

## 🔧 Configuration

### Environment Variables

The application uses environment variables for configuration. Key variables:

```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
MONGODB_URL=mongodb://admin:password123@mongodb:27017/news_db?authSource=admin
REDIS_URL=redis://:redis123@redis:6379

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
```

### Database Credentials

**MongoDB:**
- Username: `admin`
- Password: `password123`
- Database: `news_db`

**Redis:**
- Password: `redis123`

**Admin UIs:**
- MongoDB Express: `admin/admin123`
- Redis Commander: `admin/admin123`

## 🛠️ Development Mode

For development with hot reload:

```bash
# Start in development mode
./scripts/docker-setup.sh start dev
# or
scripts\docker-setup.bat start dev

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

**Development Features:**
- Hot reload enabled
- Debug port exposed (5678)
- Less secure database credentials
- Source code mounted for live editing

## 📊 Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
./scripts/docker-setup.sh logs app
./scripts/docker-setup.sh logs mongodb
./scripts/docker-setup.sh logs redis
```

### Health Checks

```bash
# Check all services
./scripts/docker-setup.sh health

# Manual health check
curl http://localhost:8000/health
```

### Resource Usage

```bash
# View resource usage
docker stats

# View container status
docker-compose ps
```

## 🔄 Common Operations

### Start Services
```bash
./scripts/docker-setup.sh start
# or
docker-compose up -d
```

### Stop Services
```bash
./scripts/docker-setup.sh stop
# or
docker-compose down
```

### Restart Services
```bash
./scripts/docker-setup.sh restart
# or
docker-compose restart
```

### Update Services
```bash
# Pull latest images and rebuild
docker-compose pull
docker-compose up --build -d
```

### Clean Up
```bash
# Remove containers, volumes, and networks
./scripts/docker-setup.sh cleanup
# or
docker-compose down -v --remove-orphans
docker system prune -f
```

## 🗄️ Data Persistence

### Volumes

The following data is persisted:

- **MongoDB Data**: `mongodb_data` volume
- **Redis Data**: `redis_data` volume
- **Application Logs**: `./logs` directory

### Backup Data

```bash
# Backup MongoDB
docker-compose exec mongodb mongodump --out /backup

# Backup Redis
docker-compose exec redis redis-cli --rdb /backup/dump.rdb
```

### Restore Data

```bash
# Restore MongoDB
docker-compose exec mongodb mongorestore /backup

# Restore Redis
docker-compose exec redis redis-cli --pipe < /backup/dump.rdb
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -tulpn | grep :8000

# Stop conflicting services or change ports in docker-compose.yml
```

#### 2. Permission Denied (Linux/Mac)
```bash
# Fix script permissions
chmod +x scripts/docker-setup.sh

# Fix volume permissions
sudo chown -R $USER:$USER ./logs
```

#### 3. Docker Not Running
```bash
# Start Docker Desktop or Docker service
# Windows/Mac: Start Docker Desktop
# Linux: sudo systemctl start docker
```

#### 4. Out of Memory
```bash
# Increase Docker memory limit in Docker Desktop settings
# Or reduce service resource usage
```

#### 5. Database Connection Issues
```bash
# Check if databases are healthy
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
docker-compose exec redis redis-cli ping

# Check logs
docker-compose logs mongodb
docker-compose logs redis
```

### Debug Mode

Enable debug logging:

```bash
# Set in .env file
DEBUG=True
LOG_LEVEL=DEBUG

# Restart services
docker-compose restart app
```

### Reset Everything

```bash
# Complete reset (WARNING: This will delete all data)
docker-compose down -v --remove-orphans
docker system prune -a -f
docker volume prune -f
```

## 🔒 Security Considerations

### Production Deployment

For production deployment:

1. **Change Default Passwords**:
   ```env
   MONGO_INITDB_ROOT_PASSWORD=your_secure_password
   REDIS_PASSWORD=your_secure_password
   ```

2. **Use HTTPS**:
   - Uncomment HTTPS configuration in `nginx.conf`
   - Add SSL certificates to `./ssl/` directory

3. **Restrict Network Access**:
   - Remove port mappings for database services
   - Use internal Docker networks only

4. **Environment Variables**:
   - Use Docker secrets or external secret management
   - Never commit `.env` files to version control

### Network Security

```yaml
# In docker-compose.yml, remove port mappings for production
services:
  mongodb:
    # ports:  # Remove this for production
    #   - "27017:27017"
```

## 📈 Performance Tuning

### Resource Limits

```yaml
# In docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### Database Optimization

```yaml
# MongoDB optimization
services:
  mongodb:
    command: mongod --wiredTigerCacheSizeGB 1
```

### Redis Optimization

```yaml
# Redis optimization
services:
  redis:
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build and Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and test
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
          ./scripts/docker-setup.sh health
          docker-compose exec app pytest
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MongoDB Docker Image](https://hub.docker.com/_/mongo)
- [Redis Docker Image](https://hub.docker.com/_/redis)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Need Help?** Check the troubleshooting section or create an issue in the repository.
