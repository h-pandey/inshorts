# Docker Build Troubleshooting Guide

## 🚨 **Issue: Docker Build Getting Stuck**

### **Problem**
Docker Compose build gets stuck at step 10/17 during Python dependency installation, specifically when building pandas and other heavy packages.

### **Root Causes**
1. **Pandas Compilation**: Pandas 2.1.4 requires compilation from source
2. **Heavy Dependencies**: `python-jose[cryptography]`, `passlib[bcrypt]` need compilation
3. **Missing Build Dependencies**: Some packages require additional system libraries
4. **Resource Intensive**: Compilation uses significant CPU and memory

---

## 🔧 **Solutions Implemented**

### **1. Optimized Dockerfile**
Created multiple Dockerfile versions:
- `Dockerfile.simple` - Minimal dependencies for quick testing
- `Dockerfile.optimized` - Uses pre-built wheels
- `Dockerfile` - Full production build

### **2. Minimal Requirements**
- `requirements-minimal.txt` - Core dependencies only
- `requirements-prod.txt` - Production dependencies without dev tools
- `requirements.txt` - Full development dependencies

### **3. Build Optimizations**
- Added `--only-binary=all` to use pre-built wheels
- Added `--no-cache-dir` to reduce image size
- Removed heavy development dependencies from production

---

## 🚀 **Quick Fix Commands**

### **Option 1: Use Simple Dockerfile (Recommended)**
```bash
# Stop current build
docker-compose down

# Clean up
docker system prune -f

# Build with simple Dockerfile
docker-compose build --no-cache

# Start services
docker-compose up -d
```

### **Option 2: Use Fix Script**
```bash
# Windows
scripts\fix-docker-build.bat

# Linux/Mac
./scripts/fix-docker-build.sh
```

### **Option 3: Manual Cleanup**
```bash
# Stop and remove containers
docker-compose down -v

# Remove images
docker rmi $(docker images -q)

# Clean build cache
docker builder prune -f

# Rebuild
docker-compose build --no-cache
```

---

## 📊 **Dockerfile Comparison**

| Dockerfile | Dependencies | Build Time | Image Size | Use Case |
|------------|-------------|------------|------------|----------|
| `Dockerfile.simple` | Minimal | ~2-3 min | ~200MB | Quick testing |
| `Dockerfile.optimized` | Production | ~5-8 min | ~300MB | Production |
| `Dockerfile` | Full | ~15-20 min | ~500MB | Development |

---

## 🔍 **Build Process Analysis**

### **What Was Causing the Hang**
1. **Pandas Compilation**: Building pandas from source takes 10-15 minutes
2. **Cryptography Dependencies**: `python-jose[cryptography]` requires OpenSSL compilation
3. **Memory Issues**: Compilation can exhaust available memory
4. **Network Timeouts**: Large package downloads can timeout

### **Optimizations Applied**
1. **Pre-built Wheels**: Use `--only-binary=all` when possible
2. **Minimal Dependencies**: Remove unnecessary packages
3. **System Libraries**: Add required build dependencies
4. **Cache Management**: Proper cache cleanup

---

## 🧪 **Testing the Fix**

### **1. Test Simple Build**
```bash
# Build with minimal dependencies
docker-compose build app

# Check build time
time docker-compose build app
```

### **2. Test Application**
```bash
# Start services
docker-compose up -d

# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs -f app
```

### **3. Verify Functionality**
```bash
# Test API endpoints
curl http://localhost:8000/
curl http://localhost:8000/docs

# Check database connection
docker-compose exec app python -c "from app.core.database import database; import asyncio; asyncio.run(database.connect())"
```

---

## 📋 **Prevention Strategies**

### **1. Use Multi-stage Builds**
- Separate build and runtime environments
- Copy only necessary files to production stage

### **2. Optimize Dependencies**
- Use specific versions
- Remove unused packages
- Use pre-built wheels when available

### **3. Build Caching**
- Order Dockerfile commands by change frequency
- Use `.dockerignore` to exclude unnecessary files
- Cache pip dependencies separately

### **4. Resource Management**
- Increase Docker memory limit
- Use `--memory` flag for builds
- Monitor build progress

---

## 🆘 **Emergency Recovery**

### **If Build Still Hangs**
1. **Kill Docker Process**
   ```bash
   # Windows
   taskkill /f /im "Docker Desktop.exe"
   
   # Linux/Mac
   sudo pkill -f docker
   ```

2. **Restart Docker Desktop**
   - Close Docker Desktop
   - Restart the application
   - Wait for full startup

3. **Use Alternative Build**
   ```bash
   # Use development Dockerfile
   docker-compose -f docker-compose.dev.yml up --build -d
   ```

### **If Memory Issues Persist**
1. **Increase Docker Resources**
   - Docker Desktop → Settings → Resources
   - Increase Memory to 4GB+
   - Increase CPU to 2+ cores

2. **Use BuildKit**
   ```bash
   export DOCKER_BUILDKIT=1
   docker-compose build
   ```

---

## ✅ **Verification Checklist**

- [ ] Docker build completes without hanging
- [ ] All services start successfully
- [ ] Application responds to health checks
- [ ] Database connections work
- [ ] API endpoints are accessible
- [ ] Logs show no errors

---

## 📞 **Next Steps**

1. **Use Simple Dockerfile** for initial testing
2. **Gradually add dependencies** as needed
3. **Monitor build times** and optimize
4. **Use production Dockerfile** for deployment

**The optimized build should complete in 2-5 minutes instead of hanging indefinitely.**
