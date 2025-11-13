import os
import sys
import time
import signal
import asyncio
import logging
import traceback
import subprocess
import threading
from pathlib import Path
from datetime import datetime

# Set console output to UTF-8
if sys.platform == 'win32':
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configure logging
LOG_FILE = "app.log"

# Clear the log file at the start of each run
with open(LOG_FILE, 'w'):
    pass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a'),  # Use 'a' mode to append to existing file
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("app")

def log_stream(stream, prefix):
    """Log output from a subprocess stream"""
    for line in iter(stream.readline, ''):
        log_line = f"{prefix} {line}".strip()
        if "ERROR" in log_line or "Exception" in log_line:
            logger.error(log_line)
        elif "WARNING" in log_line:
            logger.warning(log_line)
        else:
            logger.info(log_line)
        print(log_line)

async def check_backend_health():
    """Check if backend is running and healthy"""
    health_url = "http://localhost:8000/admin/"  # Using Django admin as health check
    max_retries = 10
    retry_delay = 2  # seconds
    
    logger.info("🔍 Checking backend health...")
    logger.debug(f"Backend health check URL: {health_url}")
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    health_url,
                    timeout=5.0,
                    follow_redirects=True
                )
                if response.status_code in [200, 302]:  # 302 for login redirect
                    logger.info("✅ Backend is running!")
                    return True
                error_msg = f"Backend returned status {response.status_code}"
                logger.warning(error_msg)
                print(f"⚠️  {error_msg}")
        except Exception as e:
            error_msg = f"Backend not available (attempt {attempt + 1}/{max_retries}): {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            print(f"❌ {error_msg}")
        
        if attempt < max_retries - 1:
            retry_msg = f"Retrying in {retry_delay} seconds..."
            logger.info(retry_msg)
            print(f"⏳ {retry_msg}")
            time.sleep(retry_delay)
    
    error_msg = "Failed to connect to the backend at http://localhost:8000"
    logger.error(error_msg)
    print(f"\n❌ {error_msg}. Please ensure the backend server is running.")
    return False

def start_backend():
    """Start the Django backend server"""
    logger.info("Starting Django Backend Server...")
    
    try:
        # Set up the environment
        env = os.environ.copy()
        # Go up one level from frontend to project root, then into backend
        backend_dir = Path(__file__).parent.parent.absolute() / 'backend'
        
        # Verify backend directory exists
        if not backend_dir.exists() or not (backend_dir / 'manage.py').exists():
            logger.error(f"Backend directory not found at: {backend_dir}")
            return None
            
        logger.info(f"Starting backend from: {backend_dir}")
        
        # Start the Django development server
        backend_process = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"],
            cwd=str(backend_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Start logging threads
        threading.Thread(
            target=log_stream, 
            args=(backend_process.stdout, "[Backend]"), 
            daemon=True
        ).start()
        
        threading.Thread(
            target=log_stream, 
            args=(backend_process.stderr, "[Backend Error]"), 
            daemon=True
        ).start()
        
        # Give backend some time to start
        time.sleep(2)
        return backend_process
        
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def run_flet():
    """Run the Flet application"""
    try:
        # Set the FLET_DEFAULT_VIEW environment variable
        os.environ["FLET_DEFAULT_VIEW"] = "web_browser"
        
        # Add frontend to Python path
        frontend_dir = Path(__file__).parent.absolute()
        sys.path.insert(0, str(frontend_dir))
        
        # Import and start the Flet app
        from src.app import main
        import flet as ft
        
        logger.info("Launching Flet application...")
        
        # Run the Flet app in the main thread
        ft.app(
            target=main,
            view=ft.WEB_BROWSER,
            port=8503,
            host="127.0.0.1",
            route_url_strategy="path"
        )
        
        # Keep the application running
        while True:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Fatal error in Flet application: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def start_frontend():
    """Start the Flet frontend application"""
    try:
        logger.info("\nStarting Frontend Application...")
        # Run the Flet app in the main thread
        run_flet()
    except Exception as e:
        logger.error(f"Failed to start frontend: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def cleanup(backend_process):
    """Cleanup function to stop the backend process"""
    if backend_process:
        logger.info("\nStopping backend server...")
        try:
            # Try to terminate gracefully
            backend_process.terminate()
            try:
                # Wait for process to terminate
                backend_process.wait(timeout=5)
                logger.info("Backend server stopped")
            except subprocess.TimeoutExpired:
                # If it doesn't terminate, force kill it
                logger.warning("Backend server did not stop gracefully, forcing kill...")
                backend_process.kill()
        except Exception as e:
            logger.error(f"Error stopping backend server: {e}")
            logger.error(traceback.format_exc())

def run_backend():
    """Run the backend server in a separate thread"""
    try:
        # Start the backend server
        backend_process = start_backend()
        if not backend_process:
            logger.error("Failed to start backend server")
            return None
        
        # Wait for backend to be ready
        logger.info("\nWaiting for backend to initialize...")
        if not asyncio.run(check_backend_health()):
            logger.error("Backend health check failed")
            return None
            
        return backend_process
    except Exception as e:
        logger.error(f"Error in backend: {str(e)}")
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    import httpx
    
    logger.info("=" * 50)
    logger.info(f"Starting Lawyer Office Management System - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set working directory to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Start the backend in a separate thread
    import threading
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give the backend a moment to start
    time.sleep(2)
    
    try:
        # Start the frontend in the main thread
        start_frontend()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    except Exception as e:
        logger.error(f"\nAn error occurred: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        # Cleanup will be handled by the daemon thread
        logger.info("Application shutdown complete")