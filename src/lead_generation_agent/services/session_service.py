"""
Session management service for handling user sessions across components
"""

import sqlite3
import uuid
import threading
import time
from typing import Optional, Dict
from datetime import datetime, timedelta
from .database_service import DATABASE_PATH, initialize_database

class SessionService:
    """Database-based session management service"""
    
    def __init__(self, db_path: str = None, cleanup_interval: int = 3600):
        """Initialize session service with database"""
        self.db_path = db_path or DATABASE_PATH
        self.cleanup_interval = cleanup_interval  # Cleanup every hour by default
        self._cleanup_thread = None
        self._stop_cleanup = False
        
        # Initialize database (only once)
        initialize_database()
        
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background thread for cleaning up expired sessions"""
        if self._cleanup_thread is None:
            self._stop_cleanup = False
            self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
            self._cleanup_thread.start()
    
    def _cleanup_worker(self):
        """Background worker for cleaning up expired sessions"""
        while not self._stop_cleanup:
            try:
                time.sleep(self.cleanup_interval)
                if not self._stop_cleanup:
                    self.cleanup_expired_sessions()
            except Exception as e:
                print(f"Session cleanup error: {e}")
    
    def stop_cleanup(self):
        """Stop the background cleanup thread"""
        self._stop_cleanup = True
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
    
    def create_session(self, user_data: dict, remember_me: bool = False) -> str:
        """Create a new session for a user"""
        session_id = str(uuid.uuid4())
        
        # Set session timeout
        if remember_me:
            expires_at = datetime.now() + timedelta(days=30)
        else:
            expires_at = datetime.now() + timedelta(hours=24)
        
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                conn.execute("""
                    INSERT INTO sessions (
                        session_id, user_id, username, email, role,
                        google_authenticated, google_email, expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    user_data.get("user_id"),
                    user_data.get("username"),
                    user_data.get("email"),
                    user_data.get("role"),
                    user_data.get("google_authenticated", False),
                    user_data.get("google_email"),
                    expires_at
                ))
                conn.commit()
            
            return session_id
        except sqlite3.Error as e:
            print(f"Error creating session: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session by session ID"""
        if not session_id:
            return None
        
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.execute("""
                    SELECT s.session_id, s.user_id, s.username, s.email, s.role,
                           s.google_authenticated, s.google_email, s.created_at, s.expires_at, s.last_activity,
                           u.google_authenticated as user_google_auth, u.google_email as user_google_email
                    FROM sessions s
                    LEFT JOIN users u ON s.user_id = u.user_id
                    WHERE s.session_id = ?
                """, (session_id,))
                row = cursor.fetchone()
            
            if not row:
                return None
            
            session_data = {
                "session_id": row[0],
                "user_id": row[1],
                "username": row[2],
                "email": row[3],
                "role": row[4],
                "google_authenticated": bool(row[5] or row[10]),  # Use user table as source of truth
                "google_email": row[6] or row[11],  # Use user table as source of truth
                "created_at": row[7],  # Already a datetime object with PARSE_DECLTYPES
                "expires_at": row[8],  # Already a datetime object with PARSE_DECLTYPES
                "last_activity": row[9]  # Already a datetime object with PARSE_DECLTYPES
            }
            
            # Check if session has expired
            if datetime.now() > session_data["expires_at"]:
                self.remove_session(session_id)
                return None
            
            # Update last activity
            self._update_last_activity(session_id)
            
            # Sync Google auth status from user table to session table
            if row[10] is not None:  # If user table has Google auth data
                self.update_google_auth_status(session_id, bool(row[10]), row[11])
            
            return session_data
        except sqlite3.Error as e:
            print(f"Error getting session: {e}")
            return None
    
    def remove_session(self, session_id: str) -> bool:
        """Remove a session"""
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error removing session: {e}")
            return False
    
    def remove_user_sessions(self, user_id: str) -> int:
        """Remove all sessions for a specific user (for logout from all devices)"""
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error removing user sessions: {e}")
            return 0
    
    def is_valid_session(self, session_id: str) -> bool:
        """Check if session is valid and not expired"""
        session = self.get_session(session_id)
        return session is not None
    
    def get_user_id(self, session_id: str) -> Optional[str]:
        """Get user ID from session"""
        session = self.get_session(session_id)
        return session.get("user_id") if session else None
    
    def get_username(self, session_id: str) -> Optional[str]:
        """Get username from session"""
        session = self.get_session(session_id)
        return session.get("username") if session else None
    
    def get_user_email(self, session_id: str) -> Optional[str]:
        """Get user email from session"""
        session = self.get_session(session_id)
        return session.get("email") if session else None
    
    def get_user_role(self, session_id: str) -> Optional[str]:
        """Get user role from session"""
        session = self.get_session(session_id)
        return session.get("role") if session else None
    
    def is_google_authenticated(self, session_id: str) -> bool:
        """Check if user has Google authentication"""
        session = self.get_session(session_id)
        return session.get("google_authenticated", False) if session else False
    
    def get_google_email(self, session_id: str) -> Optional[str]:
        """Get Google email from session"""
        session = self.get_session(session_id)
        return session.get("google_email") if session else None
    
    def update_google_auth_status(self, session_id: str, authenticated: bool, google_email: str = None) -> bool:
        """Update Google authentication status in session"""
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                conn.execute("""
                    UPDATE sessions SET 
                        google_authenticated = ?, 
                        google_email = ?,
                        last_activity = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (authenticated, google_email, session_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error updating Google auth status: {e}")
            return False
    
    def _update_last_activity(self, session_id: str):
        """Update session's last activity timestamp"""
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                conn.execute("""
                    UPDATE sessions SET last_activity = CURRENT_TIMESTAMP 
                    WHERE session_id = ?
                """, (session_id,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating last activity: {e}")
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions and return count of removed sessions"""
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.execute("""
                    DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP
                """)
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error cleaning up sessions: {e}")
            return 0
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM sessions WHERE expires_at > CURRENT_TIMESTAMP")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error getting active sessions count: {e}")
            return 0
    
    def get_user_sessions_count(self, user_id: str) -> int:
        """Get count of active sessions for a specific user"""
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM sessions 
                    WHERE user_id = ? AND expires_at > CURRENT_TIMESTAMP
                """, (user_id,))
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error getting user sessions count: {e}")
            return 0
    
    def get_all_sessions(self) -> list:
        """Get all active sessions (for admin purposes)"""
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.execute("""
                    SELECT session_id, user_id, username, email, role, created_at, expires_at, last_activity
                    FROM sessions WHERE expires_at > CURRENT_TIMESTAMP
                    ORDER BY created_at DESC
                """)
                rows = cursor.fetchall()
                
                sessions = []
                for row in rows:
                    sessions.append({
                        "session_id": row[0],
                        "user_id": row[1],
                        "username": row[2],
                        "email": row[3],
                        "role": row[4],
                        "created_at": row[5],  # Already a datetime object with PARSE_DECLTYPES
                        "expires_at": row[6],  # Already a datetime object with PARSE_DECLTYPES
                        "last_activity": row[7]  # Already a datetime object with PARSE_DECLTYPES
                    })
                
                return sessions
        except sqlite3.Error as e:
            print(f"Error getting all sessions: {e}")
            return []


# Global session service instance
session_service = SessionService() 