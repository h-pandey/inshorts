"""
Development server runner.
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings


def main():
    """Run the development server."""
    print("🚀 Starting Contextual News API development server...")
    print(f"📊 Debug mode: {settings.debug}")
    print(f"📝 Log level: {settings.log_level}")
    print(f"🌐 API docs: http://localhost:8000/docs")
    print(f"🔍 Health check: http://localhost:8000/health")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
