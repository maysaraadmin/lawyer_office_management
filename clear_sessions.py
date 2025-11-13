import os
import shutil
from pathlib import Path

def clear_sessions():
    # Clear Django session files
    session_dir = Path('backend/sessions')
    if session_dir.exists():
        shutil.rmtree(session_dir)
        print(f"Cleared session directory: {session_dir}")
    
    # Clear any cached session data
    cache_dir = Path('backend/cache')
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        print(f"Cleared cache directory: {cache_dir}")
    
    # Clear any SQLite database files (if using SQLite)
    db_file = Path('backend/db.sqlite3')
    if db_file.exists():
        os.remove(db_file)
        print(f"Removed database file: {db_file}")
    
    # Recreate the database by running migrations
    print("\nTo recreate the database, run these commands:")
    print("cd backend")
    print("python manage.py migrate")
    print("python manage.py createsuperuser")

if __name__ == "__main__":
    clear_sessions()
