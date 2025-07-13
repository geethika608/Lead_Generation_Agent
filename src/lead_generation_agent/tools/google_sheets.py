"""
Google Sheets integration tool for saving lead data and campaign information.
Supports multi-user authentication with session management.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from crewai.tools import tool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ..services.google_auth import GoogleAuthManager

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """Manages Google Sheets operations with user-specific authentication"""
    
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or 'default'
        self.auth_manager = GoogleAuthManager(user_id=user_id)
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Sheets API service with user's credentials"""
        try:
            credentials = self.auth_manager.get_credentials()
            if credentials:
                self.service = build('sheets', 'v4', credentials=credentials)
                logger.info(f"Google Sheets service initialized for user {self.user_id}")
            else:
                logger.warning(f"No user credentials available for user {self.user_id}, using placeholder mode")
                self.service = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service for user {self.user_id}: {e}")
            self.service = None
    
    def _create_spreadsheet(self, title: str) -> str:
        """Create a new Google Spreadsheet in user's account"""
        try:
            if not self.service:
                # Return placeholder ID
                return "placeholder_spreadsheet_id"
            
            spreadsheet_body = {
                'properties': {
                    'title': title
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Leads',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 10
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': 'Campaigns',
                            'gridProperties': {
                                'rowCount': 100,
                                'columnCount': 10
                            }
                        }
                    }
                ]
            }
            
            request = self.service.spreadsheets().create(body=spreadsheet_body)
            response = request.execute()
            
            logger.info(f"Created new spreadsheet for user {self.user_id}: {response['spreadsheetId']}")
            return response['spreadsheetId']
            
        except Exception as e:
            logger.error(f"Error creating spreadsheet for user {self.user_id}: {e}")
            return "error_spreadsheet_id"
    
    def _write_to_sheet(self, spreadsheet_id: str, sheet_name: str, data: List[List[Any]]) -> bool:
        """Write data to a specific sheet in user's spreadsheet"""
        try:
            if not self.service:
                logger.info(f"Placeholder for user {self.user_id}: Would write {len(data)} rows to {sheet_name}")
                return True
            
            range_name = f"{sheet_name}!A1"
            
            body = {
                'values': data
            }
            
            request = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            )
            response = request.execute()
            
            logger.info(f"Updated {response.get('updatedCells')} cells in {sheet_name} for user {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing to sheet for user {self.user_id}: {e}")
            return False

# Global sheets manager instances for different users
_sheets_managers: Dict[str, GoogleSheetsManager] = {}

def get_sheets_manager(user_id: Optional[str] = None) -> GoogleSheetsManager:
    """Get or create a sheets manager for a specific user"""
    if not user_id:
        user_id = 'default'
    
    if user_id not in _sheets_managers:
        _sheets_managers[user_id] = GoogleSheetsManager(user_id=user_id)
    
    return _sheets_managers[user_id]

@tool("google_sheets_saver")
def save_to_google_sheets(data: str, sheet_name: str = "Leads", user_id: str = "default") -> str:
    """
    Save lead data and campaign information to user's Google Sheets.
    
    Args:
        data: JSON string containing data to save
        sheet_name: Name of the sheet to write to (default: "Leads")
        user_id: User ID for authentication (default: "default")
        
    Example:
        ```json
        {
            "data": "[{\"name\": \"John Doe\", \"email\": \"john@example.com\", \"company\": \"Tech Corp\"}]",
            "sheet_name": "Leads",
            "user_id": "user123"
        }
        ```
    """
    try:
        # Debug: Log the user_id being used
        logger.info(f"Google Sheets saver called with user_id: {user_id}")
        print(f"🔐 Google Sheets saver called with user_id: {user_id}")
        
        # Get sheets manager for this user
        sheets_manager = get_sheets_manager(user_id)
        
        # Check if user is authenticated
        if not sheets_manager.service:
            return "❌ **Google Authentication Required**\n\nPlease authenticate with your Google account first using the 'Connect Google Account' button in the UI.\n\n**What you need to do**:\n1. Click 'Connect Google Account' in the UI\n2. Sign in to your Google account in the browser\n3. Grant the requested permissions\n4. Try running the workflow again"
        
        # Parse the data
        if isinstance(data, str):
            data_dict = json.loads(data)
        else:
            data_dict = data
        
        # Convert data to sheet format
        if isinstance(data_dict, list) and len(data_dict) > 0:
            # Get headers from first item
            headers = list(data_dict[0].keys())
            rows = [headers]  # Header row
            
            # Add data rows
            for item in data_dict:
                row = [str(item.get(header, '')) for header in headers]
                rows.append(row)
        else:
            # Single item or empty
            if isinstance(data_dict, dict):
                headers = list(data_dict.keys())
                rows = [headers, [str(data_dict.get(header, '')) for header in headers]]
            else:
                rows = [['Data'], [str(data_dict)]]
        
        # Create new spreadsheet
        title = f"Lead Generation Campaign - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        spreadsheet_id = sheets_manager._create_spreadsheet(title)
        
        # Validate spreadsheet ID
        if not spreadsheet_id or spreadsheet_id.startswith("placeholder_") or spreadsheet_id.startswith("error_"):
            return f"❌ Failed to create Google Spreadsheet. Please check your Google authentication and try again."
        
        # Write data to sheet
        success = sheets_manager._write_to_sheet(spreadsheet_id, sheet_name, rows)
        
        if success:
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            records_count = len(rows) - 1 if len(rows) > 1 else 0

            print(f"✅ Data successfully saved to your Google Sheets\n📊 Spreadsheet URL: {spreadsheet_url}\n📋 Sheet: {sheet_name}\n📈 Records saved: {records_count}")
            
            return f"✅ Data successfully saved to your Google Sheets\n📊 Spreadsheet URL: {spreadsheet_url}\n📋 Sheet: {sheet_name}\n📈 Records saved: {records_count}"
        else:
            return f"❌ Failed to write data to your Google Sheets. Please check your Google authentication and try again."
        
    except Exception as e:
        logger.error(f"Error saving to Google Sheets for user {user_id}: {e}")
        return f"❌ Failed to save data to your Google Sheets: {str(e)}" 