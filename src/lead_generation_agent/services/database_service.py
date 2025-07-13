"""
Database service for the Lead Generation Agent
"""

import os
import sqlite3
from pathlib import Path

# Get the project root directory (Lead_Generation_Agent folder)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Database path in the data folder
DATABASE_PATH = os.path.join(PROJECT_ROOT, "data", "lead_generation_agent.db")

# Ensure data directory exists
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def is_database_initialized():
    """Check if the database has been initialized by checking if required tables exist"""
    try:
        with sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            # Check if both required tables exist
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('sessions', 'users')")
            tables = [row[0] for row in cursor.fetchall()]
            
            return len(tables) >= 2  # Both tables must exist
    except Exception:
        return False

def initialize_database():
    """Initialize the database with all required tables (only creates if they don't exist)"""
    # Check if database is already initialized
    if is_database_initialized():
        return  # Tables already exist, nothing to do
    
    try:
        with sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            # Create sessions table (IF NOT EXISTS handles the check)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL,
                    role TEXT NOT NULL,
                    google_authenticated BOOLEAN DEFAULT FALSE,
                    google_email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create users table (IF NOT EXISTS handles the check)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    status TEXT NOT NULL DEFAULT 'active',
                    google_authenticated BOOLEAN DEFAULT FALSE,
                    google_email TEXT,
                    google_token_file TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    company TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for faster lookups (IF NOT EXISTS handles the check)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_user_id 
                ON sessions (user_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_expires_at 
                ON sessions (expires_at)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_last_activity 
                ON sessions (last_activity)
            """)
            
            conn.commit()
            
        print(f"Database initialized successfully at: {DATABASE_PATH}")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise 