"""
Google Workspace integration tools for data storage.
This module provides convenient imports from the separate Google tools.
"""

# Import the authentication manager
from .google_auth import GoogleAuthManager

# Import Google Sheets functionality
from .google_sheets import save_to_google_sheets

# Re-export for backward compatibility
__all__ = [
    'GoogleAuthManager',
    'save_to_google_sheets'
] 