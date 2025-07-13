"""
Google Docs integration tool for saving campaign reports and documentation.
Supports multi-user authentication with session management.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from crewai.tools import tool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..services.google_auth import GoogleAuthManager

logger = logging.getLogger(__name__)

class GoogleDocsManager:
    """Manages Google Docs operations with user-specific authentication"""
    
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or 'default'
        self.auth_manager = GoogleAuthManager(user_id=user_id)
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Docs API service with user's credentials"""
        try:
            credentials = self.auth_manager.get_credentials()
            if credentials:
                self.service = build('docs', 'v1', credentials=credentials)
                logger.info(f"Google Docs service initialized for user {self.user_id}")
            else:
                logger.warning(f"No user credentials available for user {self.user_id}, using placeholder mode")
                self.service = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Docs service for user {self.user_id}: {e}")
            self.service = None
    
    def _create_document(self, title: str) -> str:
        """Create a new Google Document in user's account"""
        try:
            if not self.service:
                # Return placeholder ID
                return "placeholder_document_id"
            
            document_body = {
                'title': title
            }
            
            request = self.service.documents().create(body=document_body)
            document = request.execute()
            
            document_id = document.get('documentId')
            logger.info(f"Created new document for user {self.user_id}: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error creating document for user {self.user_id}: {e}")
            return "error_document_id"
    
    def _write_to_document(self, document_id: str, content: str) -> bool:
        """Write content to a Google Document"""
        try:
            if not self.service:
                logger.info(f"Placeholder for user {self.user_id}: Would write content to document")
                return True
            
            # Prepare the content for insertion
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': content
                    }
                }
            ]
            
            request = self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            )
            response = request.execute()
            
            logger.info(f"Updated document for user {self.user_id}: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing to document for user {self.user_id}: {e}")
            return False

# Global docs manager instances for different users
_docs_managers: Dict[str, GoogleDocsManager] = {}

def get_docs_manager(user_id: Optional[str] = None) -> GoogleDocsManager:
    """Get or create a docs manager for a specific user"""
    if not user_id:
        user_id = 'default'
    
    if user_id not in _docs_managers:
        _docs_managers[user_id] = GoogleDocsManager(user_id=user_id)
    
    return _docs_managers[user_id]

@tool("google_docs_saver")
def save_to_google_docs(content: str, document_title: str = "Campaign Report", user_id: Optional[str] = None) -> str:
    """
    Save campaign reports and documentation to user's Google Docs.
    
    Args:
        content: Content to save to the document
        document_title: Title for the new document
        user_id: User ID for authentication (optional)
        
    Example:
        ```json
        {
            "content": "# Campaign Report\n\nThis is a sample campaign report.",
            "document_title": "Q1 Campaign Report"
        }
        ```
    """
    try:
        # Debug: Log the user_id being used
        logger.info(f"Google Docs saver called with user_id: {user_id}")
        print(f"🔐 Google Docs saver called with user_id: {user_id}")
        
        # Get docs manager for this user
        docs_manager = get_docs_manager(user_id)
        
        # Check if user is authenticated
        if not docs_manager.service:
            return "❌ **Google Authentication Required**\n\nPlease authenticate with your Google account first using the 'Connect Google Account' button in the UI.\n\n**What you need to do**:\n1. Click 'Connect Google Account' in the UI\n2. Sign in to your Google account in the browser\n3. Grant the requested permissions\n4. Try running the workflow again"
        
        # Create new document
        document_id = docs_manager._create_document(document_title)
        
        # Validate document ID
        if not document_id or document_id.startswith("placeholder_") or document_id.startswith("error_"):
            return f"❌ Failed to create Google Document. Please check your Google authentication and try again."
        
        # Write content to document
        success = docs_manager._write_to_document(document_id, content)
        
        if success:
            document_url = f"https://docs.google.com/document/d/{document_id}"
            return f"✅ Document successfully saved to your Google Docs\n📄 Document URL: {document_url}\n📝 Title: {document_title}"
        else:
            return f"❌ Failed to write content to your Google Document. Please check your Google authentication and try again."
        
    except Exception as e:
        logger.error(f"Error saving to Google Docs for user {user_id}: {e}")
        return f"❌ Failed to save document to your Google Docs: {str(e)}" 