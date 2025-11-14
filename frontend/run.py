import os
import sys
import time
import signal
import asyncio
import logging
import traceback
import subprocess
import threading
import httpx
import uvicorn
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Callable, Any

# Enable tracemalloc for better error tracking
import tracemalloc
tracemalloc.start()

class EmojiSafeHandler(logging.StreamHandler):
    """Custom handler to safely log emoji characters to Windows console"""
    def emit(self, record):
        try:
            msg = self.format(record)
            # Replace emoji with text equivalents for Windows console
            emoji_map = {
                '✅': '[OK]',
                '❌': '[ERROR]',
                '🔄': '[REFRESH]',
                '🖥️': '[FRONTEND]',
                '🧹': '[CLEANUP]',
                '👋': ''
            }
            for emoji, text in emoji_map.items():
                msg = msg.replace(emoji, text)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

def setup_logging():
    """Configure application logging"""
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler with emoji-safe formatter
    console_handler = EmojiSafeHandler()
    console_handler.setFormatter(formatter)
    
    # Create file handler
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, file_handler]
    )
    
    return logging.getLogger("app")

# Initialize logging
logger = setup_logging()

class ProcessLogger:
    """Handle logging for subprocess output"""
    
    def __init__(self, stream, prefix: str, log_level: int = logging.INFO):
        self.stream = stream
        self.prefix = prefix
        self.log_level = log_level
        self._stop_event = threading.Event()
    
    def log_line(self, line: str) -> None:
        """Log a single line with appropriate log level"""
        line = line.strip()
        if not line:
            return
            
        log_line = f"{self.prefix} {line}"
        
        # Determine log level
        if any(err in line.upper() for err in ['ERROR', 'EXCEPTION', 'CRITICAL']):
            logger.error(log_line)
        elif 'WARNING' in line.upper():
            logger.warning(log_line)
        elif 'DEBUG' in line.upper():
            logger.debug(log_line)
        else:
            logger.log(self.log_level, log_line)
    
    def run(self) -> None:
        """Run the logger in a loop"""
        try:
            for line in iter(self.stream.readline, ''):
                if self._stop_event.is_set():
                    break
                self.log_line(line)
        except Exception as e:
            logger.error(f"Error in process logger: {e}")
    
    def stop(self) -> None:
        """Stop the logger"""
        self._stop_event.set()

def cleanup(backend_process):
    """Cleanup function to stop the backend process"""
    if backend_process:
        logger.info("\nStopping backend server...")
        try:
            # Try to terminate gracefully
            if sys.platform == 'win32':
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(backend_process.pid)], 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                backend_process.terminate()
                try:
                    backend_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    backend_process.kill()
            logger.info("Backend server stopped")
        except Exception as e:
            logger.error(f"Error stopping backend: {e}")

def initialize_backend_api():
    """Initialize the backend API by running migrations and collecting static files"""
    try:
        # Get the backend directory
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
        
        logger.info("Initializing backend API...")
        
        # Run migrations
        logger.info("Running database migrations...")
        migrate_cmd = [sys.executable, 'manage.py', 'migrate']
        result = subprocess.run(
            migrate_cmd,
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            logger.warning(f"Migration warnings: {result.stderr}")
        else:
            logger.info("Database migrations completed successfully")
        
        # Collect static files (optional, for production)
        logger.info("Collecting static files...")
        collectstatic_cmd = [sys.executable, 'manage.py', 'collectstatic', '--noinput']
        result = subprocess.run(
            collectstatic_cmd,
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            logger.warning(f"Static files collection warnings: {result.stderr}")
        else:
            logger.info("Static files collected successfully")
        
        # Create superuser if it doesn't exist (for initial setup)
        logger.info("Checking for superuser...")
        createsuperuser_cmd = [sys.executable, 'manage.py', 'shell', '-c', 
            "from django.contrib.auth import get_user_model; "
            "User = get_user_model(); "
            "User.objects.filter(is_superuser=True).exists() or "
            "User.objects.create_superuser('admin@lawyer.com', 'admin123')"]
        result = subprocess.run(
            createsuperuser_cmd,
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            logger.info("Superuser setup completed")
        else:
            logger.info("Superuser already exists or setup not needed")
        
        logger.info("Backend API initialization completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Backend API initialization timed out")
        return False
    except Exception as e:
        logger.error(f"Error initializing backend API: {e}")
        return False

def is_backend_running():
    """Check if backend server is already running"""
    import httpx
    
    try:
        with httpx.Client(timeout=2) as client:
            response = client.get("http://127.0.0.1:8000/")
            if response.status_code == 200:
                logger.info("Backend server is already running")
                return True
    except:
        pass
    
    return False

def wait_for_backend_api(timeout: int = 30):
    """Wait for the backend API to be ready"""
    import httpx
    import time
    
    logger.info("Waiting for backend API to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Try to connect to the backend API health endpoint
            with httpx.Client(timeout=2) as client:
                # First check if Django server is responding
                response = client.get("http://127.0.0.1:8000/")
                if response.status_code in [200, 302]:
                    logger.info("Django server is responding...")
                    
                    # Now check if API health endpoint is available
                    try:
                        api_response = client.get("http://127.0.0.1:8000/api/v1/health/")
                        if api_response.status_code == 200:
                            logger.info("Backend API is ready!")
                            return True
                        elif api_response.status_code == 404:
                            logger.warning("Health endpoint not found, trying auth endpoint...")
                            # Try auth endpoint as fallback
                            auth_response = client.get("http://127.0.0.1:8000/api/v1/auth/")
                            if auth_response.status_code in [200, 401, 405]:  # 405 means endpoint exists but wrong method
                                logger.info("Backend API is ready!")
                                return True
                    except Exception as e:
                        logger.debug(f"API endpoint not yet available: {str(e)}")
                        
        except Exception as e:
            logger.debug(f"Backend not ready yet: {str(e)}")
        
        time.sleep(1)
    
    # Try one more time with detailed error
    try:
        with httpx.Client(timeout=5) as client:
            response = client.get("http://127.0.0.1:8000/api/v1/health/")
            if response.status_code == 200:
                logger.info("Backend API is ready!")
                return True
            else:
                logger.error(f"Backend API health check returned status {response.status_code}")
                logger.error(f"Response: {response.text}")
    except Exception as e:
        logger.error(f"Failed to connect to backend API: {str(e)}")
    
    raise RuntimeError(f"Backend API did not become ready within {timeout} seconds")

def run_backend_in_thread():
    """Run the backend server in a separate process"""
    try:
        # Get the backend directory
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
        
        # Set up environment variables
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        # Start the Django development server
        cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000', '--noreload']
        
        logger.info(f"Starting backend server in {backend_dir}")
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )
        
        # Log output in a separate thread
        def log_output():
            try:
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        logger.info(f"[Backend] {output.strip()}")
            except Exception as e:
                logger.error(f"Error in log output: {e}")
        
        log_thread = threading.Thread(target=log_output, daemon=True)
        log_thread.start()
        
        # Give the server time to start
        time.sleep(3)
        
        # Check if the process is still running
        if process.poll() is not None:
            raise RuntimeError("Backend server failed to start")
            
        # Wait for API to be ready
        wait_for_backend_api()
        
        logger.info("Backend server started successfully")
        return process
        
    except Exception as e:
        logger.error(f"Error starting backend server: {e}")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
        raise

def run_flet_app():
    """Run the Flet application with hot reload"""
    import flet as ft
    from src.app import main as flet_main
    
    async def on_page_init(page: ft.Page):
        try:
            # Ensure page is properly initialized
            if not hasattr(page, 'views'):
                page.views = []
            
            # Set page properties
            page.title = "Lawyer Office Management"
            page.theme_mode = ft.ThemeMode.LIGHT
            page.padding = 0
            page.window_width = 1280
            page.window_height = 800
            page.window_resizable = True
            
            # Initialize the app with the page
            try:
                await flet_main(page)
                
                # Ensure app is properly initialized
                if not hasattr(page, 'app'):
                    from src.app import LawyerOfficeApp
                    page.app = LawyerOfficeApp(page)
                
                # Show login if not authenticated
                if not getattr(page.app, 'is_authenticated', True):
                    await page.app.show_login()
                    
            except Exception as e:
                logger.error(f"❌ Error in flet_main: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Show error to user
                error_dialog = ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text("An error occurred while initializing the application."),
                    actions=[
                        ft.TextButton("OK", on_click=lambda _: page.close_dialog())
                    ]
                )
                page.dialog = error_dialog
                try:
                    page.update()
                except:
                    # If sync update fails, try async if available
                    if hasattr(page, 'update_async'):
                        await page.update_async()
                
        except Exception as e:
            logger.error(f"❌ Error initializing page: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    # Enable hot reload
    ft.app(
        target=on_page_init,
        view=ft.WEB_BROWSER,
        port=8503,
        host="127.0.0.1",
        use_color_emoji=True,
        assets_dir="assets"
    )

def main():
    """Main entry point for the application"""
    backend_process = None
    
    try:
        # Set up logging
        logger = setup_logging()
        
        logger.info("=" * 80)
        logger.info(f"🚀 Starting Lawyer Office Management System - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        try:
            # Check if backend is already running
            if is_backend_running():
                logger.info("Backend server is already running, proceeding to start frontend...")
                backend_process = None
            else:
                # Initialize the backend API first
                if not initialize_backend_api():
                    raise RuntimeError("Failed to initialize backend API")
                
                # Start backend server
                logger.info("\n🔄 Starting backend server...")
                backend_process = run_backend_in_thread()
                
                # Give the backend some time to start
                time.sleep(2)
                
                # Check if backend is running
                if backend_process.poll() is not None:
                    raise RuntimeError("Backend server failed to start")
            
            # Start frontend
            logger.info("\n🖥️  Starting frontend application...")
            run_flet_app()
            
            logger.info("\n✅ Application started successfully!")
            return 0
            
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutdown signal received...")
            return 0
        except Exception as e:
            logger.error(f"❌ Error in main: {str(e)}")
            logger.error(traceback.format_exc())
            return 1
        finally:
            logger.info("\n🧹 Cleaning up resources...")
            if backend_process and backend_process.poll() is None:
                backend_process.terminate()
            logger.info("✅ Cleanup complete. Goodbye! 👋")
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())