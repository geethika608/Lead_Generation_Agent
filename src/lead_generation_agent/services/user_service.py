"""
User management service for user profile operations and user data management
"""

import sqlite3
import bcrypt
import uuid
from datetime import datetime
from typing import Optional, List

from ..models.user_models import (
    User, UserRegistration, UserProfile, UserRole, UserStatus
)
from .database_service import DATABASE_PATH, initialize_database

class UserService:
    """Service for user management operations"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        
        # Initialize database (only once)
        initialize_database()
    
    
    def register_user(self, registration_data: UserRegistration) -> User:
        """Register a new user"""
        # Check if username or email already exists
        if self._get_user_by_username_or_email(registration_data.username):
            raise ValueError("Username already exists")
        if self._get_user_by_username_or_email(registration_data.email):
            raise ValueError("Email already exists")
        
        # Hash the password
        password_hash = bcrypt.hashpw(
            registration_data.password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create user account
        user_account = User(
            user_id=str(uuid.uuid4()),
            username=registration_data.username.lower(),
            email=registration_data.email.lower(),
            password_hash=password_hash,
            first_name=registration_data.first_name,
            last_name=registration_data.last_name,
            company=registration_data.company,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save to database
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.execute("""
                INSERT INTO users (
                    user_id, username, email, password_hash, role, status,
                    first_name, last_name, company, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_account.user_id, user_account.username, user_account.email,
                user_account.password_hash, user_account.role.value, user_account.status.value,
                user_account.first_name, user_account.last_name, user_account.company,
                user_account.created_at, user_account.updated_at
            ))
            conn.commit()
        
        return user_account
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username/email and password"""
        user = self._get_user_by_username_or_email(username)
        if not user:
            return None
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Update last login
            self._update_last_login(user.user_id)
            return user
        
        return None
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user ID"""
        user = self._get_user_by_id(user_id)
        if not user:
            return None
        
        return UserProfile(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            company=user.company,
            role=user.role,
            status=user.status,
            google_authenticated=user.google_authenticated,
            google_email=user.google_email,
            created_at=user.created_at,
            last_login=user.last_login
        )
    
    def update_user_profile(self, user_id: str, **updates) -> Optional[User]:
        """Update user profile information"""
        user = self._get_user_by_id(user_id)
        if not user:
            return None
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'company']
        update_data = {}
        
        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                update_data[field] = value
        
        if not update_data:
            return user
        
        # Update database
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            set_clause = ", ".join([f"{field} = ?" for field in update_data.keys()])
            set_clause += ", updated_at = ?"
            values = list(update_data.values()) + [datetime.now()]
            
            conn.execute(f"""
                UPDATE users SET {set_clause} WHERE user_id = ?
            """, values + [user_id])
            conn.commit()
        
        # Return updated user
        return self._get_user_by_id(user_id)
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self._get_user_by_id(user_id)
        if not user:
            return False
        
        # Verify current password
        if not bcrypt.checkpw(current_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return False
        
        # Hash new password
        new_password_hash = bcrypt.hashpw(
            new_password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Update database
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.execute("""
                UPDATE users SET password_hash = ?, updated_at = ? WHERE user_id = ?
            """, (new_password_hash, datetime.now(), user_id))
            conn.commit()
        
        return True
    
    def update_google_auth_status(self, user_id: str, authenticated: bool, google_email: str = None) -> bool:
        """Update user's Google authentication status"""
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.execute("""
                UPDATE users SET 
                    google_authenticated = ?, 
                    google_email = ?,
                    updated_at = ? 
                WHERE user_id = ?
            """, (authenticated, google_email, datetime.now(), user_id))
            conn.commit()
        return True
    
    def get_all_users(self) -> List[User]:
        """Get all users (admin only)"""
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.execute("SELECT * FROM users ORDER BY created_at DESC")
            rows = cursor.fetchall()
        
        users = []
        for row in rows:
            users.append(self._row_to_user(row))
        
        return users
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user (admin only)"""
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def _update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.execute("""
                UPDATE users SET last_login = ? WHERE user_id = ?
            """, (datetime.now(), user_id))
            conn.commit()
    
    def _get_user_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Get user by username or email"""
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.execute("""
                SELECT * FROM users WHERE username = ? OR email = ?
            """, (identifier.lower(), identifier.lower()))
            row = cursor.fetchone()
        
        if row:
            return self._row_to_user(row)
        return None
    
    def _row_to_user(self, row) -> User:
        """Convert database row to User object"""
        return User(
            user_id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            role=UserRole(row[4]),
            status=UserStatus(row[5]),
            google_authenticated=bool(row[6]),
            google_email=row[7],
            google_token_file=row[8],
            first_name=row[9],
            last_name=row[10],
            company=row[11],
            created_at=row[12],  # Already a datetime object with PARSE_DECLTYPES
            last_login=row[13],  # Already a datetime object with PARSE_DECLTYPES
            updated_at=row[14]  # Already a datetime object with PARSE_DECLTYPES
        )
    
    def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user ID"""
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
        
        if row:
            return self._row_to_user(row)
        return None 