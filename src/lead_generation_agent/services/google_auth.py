"""
Google OAuth2 authentication manager for user-specific Google Workspace integration
"""

import os
import json
import sqlite3
import logging
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from .database_service import DATABASE_PATH

logger = logging.getLogger(__name__)

class GoogleAuthManager:
    """Manages Google OAuth2 authentication for individual users"""
    
    # Google API scopes for Sheets and Docs
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/userinfo.email',
        'openid'
    ]
    
    def __init__(self, user_id: Optional[str] = None, db_path: str = None):
        """Initialize Google Auth Manager"""
        self.user_id = user_id or 'default'
        self.db_path = db_path or DATABASE_PATH
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables for Google tokens"""
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        # Create Google tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS google_tokens (
                user_id TEXT PRIMARY KEY,
                token_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                refresh_token TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Create Google auth audit table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS google_auth_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def authenticate_user(self, user_id: str) -> bool:
        """
        Authenticate user with Google using automatic OAuth2 flow
        
        Args:
            user_id: User ID to authenticate
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Check if credentials file exists
            if not os.path.exists(self.credentials_file):
                logger.error(f"Google credentials file not found: {self.credentials_file}")
                self._log_audit(user_id, "authenticate", "failed", "Credentials file not found")
                return False
            
            # Create flow
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, 
                self.SCOPES
            )
            
            # Run the flow (this will open browser automatically)
            credentials = flow.run_local_server(port=0)
            
            # Store token in database
            success = self._store_token(user_id, credentials)
            
            if success:
                self._log_audit(user_id, "authenticate", "success", "OAuth2 flow completed")
                logger.info(f"Google authentication successful for user {user_id}")
                return True
            else:
                self._log_audit(user_id, "authenticate", "failed", "Token storage failed")
                return False
                
        except Exception as e:
            logger.error(f"Google authentication failed for user {user_id}: {e}")
            self._log_audit(user_id, "authenticate", "failed", str(e))
            return False
    
    def get_credentials(self, user_id: Optional[str] = None) -> Optional[Credentials]:
        """
        Get stored credentials for user
        
        Args:
            user_id: User ID (uses self.user_id if not provided)
            
        Returns:
            Google credentials object or None if not found/expired
        """
        user_id = user_id or self.user_id
        
        try:
            conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT token_data, expires_at, refresh_token 
                FROM google_tokens 
                WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            token_data = json.loads(row[0])
            expires_at = row[1]
            refresh_token = row[2]
            
            # Get stored scopes
            stored_scopes = token_data.get('scopes', self.SCOPES)
            
            # Check if scopes match current requirements
            if set(stored_scopes) != set(self.SCOPES):
                logger.warning(f"Scope mismatch for user {user_id}. Stored: {stored_scopes}, Required: {self.SCOPES}")
                # Remove the token to force re-authentication
                self._remove_token(user_id)
                return None
            
            # Create credentials object
            credentials = Credentials(
                token=token_data.get('token'),
                refresh_token=refresh_token,
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=stored_scopes
            )
            
            # Check if token is expired and refresh if needed
            if credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    # Update stored token
                    self._store_token(user_id, credentials)
                except Exception as e:
                    logger.error(f"Failed to refresh token for user {user_id}: {e}")
                    return None
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error getting credentials for user {user_id}: {e}")
            return None
    
    def revoke_authentication(self, user_id: str) -> bool:
        """
        Revoke Google authentication for user
        
        Args:
            user_id: User ID to revoke authentication for
            
        Returns:
            True if revocation successful, False otherwise
        """
        try:
            # Get credentials to revoke
            credentials = self.get_credentials(user_id)
            if credentials:
                try:
                    # Revoke the token
                    credentials.revoke(Request())
                except Exception as e:
                    logger.warning(f"Failed to revoke token on Google side: {e}")
            
            # Remove from database
            deleted = self._remove_token(user_id)
            
            if deleted:
                self._log_audit(user_id, "revoke", "success", "Authentication revoked")
                logger.info(f"Google authentication revoked for user {user_id}")
                return True
            else:
                self._log_audit(user_id, "revoke", "failed", "No token found to revoke")
                return False
                
        except Exception as e:
            logger.error(f"Error revoking authentication for user {user_id}: {e}")
            self._log_audit(user_id, "revoke", "failed", str(e))
            return False
    
    def is_authenticated(self, user_id: Optional[str] = None) -> bool:
        """
        Check if user is authenticated with Google
        
        Args:
            user_id: User ID to check (uses self.user_id if not provided)
            
        Returns:
            True if authenticated, False otherwise
        """
        user_id = user_id or self.user_id
        credentials = self.get_credentials(user_id)
        return credentials is not None and not credentials.expired
    

    
    def _store_token(self, user_id: str, credentials: Credentials) -> bool:
        """
        Store Google token in database
        
        Args:
            user_id: User ID
            credentials: Google credentials object
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # Prepare token data
            token_data = {
                'token': credentials.token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            
            # Calculate expiration
            expires_at = None
            if credentials.expiry:
                expires_at = credentials.expiry.isoformat()
            
            conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            
            # Insert or update token
            cursor.execute('''
                INSERT OR REPLACE INTO google_tokens 
                (user_id, token_data, expires_at, refresh_token, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                user_id,
                json.dumps(token_data),
                expires_at,
                credentials.refresh_token
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing token for user {user_id}: {e}")
            return False
    
    def _remove_token(self, user_id: str) -> bool:
        """
        Remove Google token from database
        
        Args:
            user_id: User ID
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM google_tokens WHERE user_id = ?', (user_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            if deleted:
                logger.info(f"Token removed for user {user_id}")
                return True
            else:
                logger.warning(f"No token found to remove for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing token for user {user_id}: {e}")
            return False
    
    def clear_all_tokens(self) -> bool:
        """
        Clear all Google tokens from database (useful for scope changes)
        
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM google_tokens')
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleared {deleted_count} Google tokens from database")
            return True
                
        except Exception as e:
            logger.error(f"Error clearing all tokens: {e}")
            return False
    
    def _log_audit(self, user_id: str, action: str, status: str, details: str = None):
        """
        Log authentication audit event
        
        Args:
            user_id: User ID
            action: Action performed
            status: Success/failure status
            details: Additional details
        """
        try:
            conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO google_auth_audit 
                (user_id, action, status, details)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, status, details))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
    
 