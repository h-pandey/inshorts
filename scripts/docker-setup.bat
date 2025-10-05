@echo off
REM Docker setup script for Contextual News API (Windows)
REM This script helps set up and manage the Docker environment

setlocal enabledelayedexpansion

REM Function to print colored output (simplified for Windows)
:print_status
echo [INFO] %~1
goto :eof

:print_success
echo [SUCCESS] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

REM Function to check if Docker is installed
:check_docker
docker --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker is not installed. Please install Docker Desktop first."
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker Compose is not installed. Please install Docker Desktop first."
    exit /b 1
)

call :print_success "Docker and Docker Compose are installed"
goto :eof

REM Function to create .env file if it doesn't exist
:create_env_file
if not exist .env (
    call :print_status "Creating .env file from template..."
    copy env.example .env >nul
    call :print_warning "Please update .env file with your OpenAI API key and other configuration"
    call :print_warning "At minimum, set: OPENAI_API_KEY=your_key_here"
) else (
    call :print_success ".env file already exists"
)
goto :eof

REM Function to build and start services
:start_services
set mode=%1
if "%mode%"=="" set mode=production

call :print_status "Starting services in %mode% mode..."

if "%mode%"=="development" (
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
) else (
    docker-compose up --build -d
)

if errorlevel 1 (
    call :print_error "Failed to start services"
    exit /b 1
)

call :print_success "Services started successfully"
goto :eof

REM Function to stop services
:stop_services
call :print_status "Stopping services..."
docker-compose down
call :print_success "Services stopped"
goto :eof

REM Function to show logs
:show_logs
set service=%1
if "%service%"=="" set service=app
call :print_status "Showing logs for %service% service..."
docker-compose logs -f %service%
goto :eof

REM Function to check service health
:check_health
call :print_status "Checking service health..."

REM Wait for services to be ready
timeout /t 10 /nobreak >nul

REM Check app health
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    call :print_error "Application health check failed"
) else (
    call :print_success "Application is healthy"
)

REM Check MongoDB
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" >nul 2>&1
if errorlevel 1 (
    call :print_error "MongoDB health check failed"
) else (
    call :print_success "MongoDB is healthy"
)

REM Check Redis
docker-compose exec redis redis-cli ping >nul 2>&1
if errorlevel 1 (
    call :print_error "Redis health check failed"
) else (
    call :print_success "Redis is healthy"
)
goto :eof

REM Function to show service URLs
:show_urls
call :print_status "Service URLs:"
echo   📊 Application: http://localhost:8000
echo   📚 API Docs: http://localhost:8000/docs
echo   🔍 Health Check: http://localhost:8000/health
echo   🗄️  MongoDB Admin: http://localhost:8081 (admin/admin123)
echo   🔴 Redis Admin: http://localhost:8082 (admin/admin123)
echo.
call :print_status "Database Connection Details:"
echo   MongoDB: mongodb://admin:password123@localhost:27017/news_db?authSource=admin
echo   Redis: redis://:redis123@localhost:6379
goto :eof

REM Function to clean up
:cleanup
call :print_status "Cleaning up Docker resources..."
docker-compose down -v --remove-orphans
docker system prune -f
call :print_success "Cleanup completed"
goto :eof

REM Function to show help
:show_help
echo Docker Setup Script for Contextual News API
echo.
echo Usage: %0 [COMMAND]
echo.
echo Commands:
echo   start [dev^|prod]  Start services (default: prod)
echo   stop             Stop services
echo   restart          Restart services
echo   logs [service]   Show logs (default: app)
echo   health           Check service health
echo   urls             Show service URLs
echo   cleanup          Clean up Docker resources
echo   help             Show this help message
echo.
echo Examples:
echo   %0 start dev     Start in development mode
echo   %0 logs mongodb  Show MongoDB logs
echo   %0 health        Check all services
goto :eof

REM Main script logic
:main
set command=%1
if "%command%"=="" set command=help

if "%command%"=="start" (
    call :check_docker
    call :create_env_file
    call :start_services %2
    call :check_health
    call :show_urls
) else if "%command%"=="stop" (
    call :stop_services
) else if "%command%"=="restart" (
    call :stop_services
    call :start_services %2
    call :check_health
    call :show_urls
) else if "%command%"=="logs" (
    call :show_logs %2
) else if "%command%"=="health" (
    call :check_health
) else if "%command%"=="urls" (
    call :show_urls
) else if "%command%"=="cleanup" (
    call :cleanup
) else (
    call :show_help
)

goto :eof

REM Run main function
call :main %*
