"""
Authentication service for login, logout, and session management
"""

import sqlite3
import bcrypt
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional

from ..models.user_models import (
    UserLogin, UserRole
)
from .user_service import UserService
from .database_service import DATABASE_PATH


class AuthService:
    """Authentication service for login, logout, and session management"""
    
    def __init__(self, db_path: str = None):
        """Initialize authentication service"""
        self.db_path = db_path or DATABASE_PATH
        self.user_service = UserService(self.db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with session tables"""
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                google_authenticated BOOLEAN DEFAULT FALSE,
                google_email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                preferences TEXT DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Add preferences column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE sessions ADD COLUMN preferences TEXT DEFAULT '{}'")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists, ignore error
            pass
        
        conn.commit()
        conn.close()
    
    def login_user(self, login_data: UserLogin):
        """Authenticate user and create session"""
        # Find user by username or email
        user = self.user_service._get_user_by_username_or_email(login_data.username)
        if not user:
            raise ValueError("Invalid username or password")
        
        # Verify password
        if not bcrypt.checkpw(login_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
            raise ValueError("Invalid username or password")
        
        # Check if account is active
        if user.status.value != 'active':
            raise ValueError("Account is not active")
        
        # Create session (no remember_me functionality for now)
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(days=30)  # Default 30-day expiration
        
        # Save session to database
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (
                session_id, user_id, username, email, role, google_authenticated,
                google_email, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, user.user_id, user.username, user.email,
            user.role, user.google_authenticated, user.google_email,
            expires_at
        ))
        
        conn.commit()
        conn.close()
        
        # Update last login
        self.user_service._update_last_login(user.user_id)
        
        return session_id
    
    def logout_user(self, session_id: str) -> bool:
        """Logout user by removing session"""
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session by session ID"""
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, user_id, username, email, role, google_authenticated,
                   google_email, created_at, last_activity, expires_at, preferences
            FROM sessions WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        session_id, user_id, username, email, role, google_authenticated, \
        google_email, created_at, last_activity, expires_at, preferences = row
        
        # Parse preferences
        try:
            prefs = json.loads(preferences) if preferences else {}
        except:
            prefs = {}
        
        return {
            'session_id': session_id,
            'user_id': user_id,
            'username': username,
            'email': email,
            'role': UserRole(role).name,
            'google_authenticated': bool(google_authenticated),
            'google_email': google_email,
            'created_at': created_at,  # Already a datetime object with PARSE_DECLTYPES
            'last_activity': last_activity,  # Already a datetime object with PARSE_DECLTYPES
            'expires_at': expires_at,  # Already a datetime object with PARSE_DECLTYPES
            'preferences': prefs
        }
    
    def login(self, username: str, password: str) -> Optional[str]:
        """Simple login method that returns session_id or None"""
        try:
            from ..models.user_models import UserLogin
            # Convert username to lowercase to match user service behavior
            username_lower = username.lower()
            login_data = UserLogin(username=username_lower, password=password)
            return self.login_user(login_data)
        except ValueError as e:
            return None
        except Exception as e:
            return None
    
    def validate_session(self, session_id: str) -> bool:
        """Validate if a session exists and is not expired"""
        if not session_id:
            return False
        
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Check if session is expired
        if session['expires_at'] and session['expires_at'] < datetime.now():
            return False
        
        return True
    
    def logout(self, session_id: str) -> bool:
        """Simple logout method"""
        return self.logout_user(session_id) 