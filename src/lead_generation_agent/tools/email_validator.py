"""
Email validation tool using EmailListVerify API for spam trap detection and deliverability analysis.
"""

import json
from typing import List, Dict, Optional, Union
from crewai.tools import tool
from ..services.email_service import EmailService

# Global email service instance
_email_service = EmailService()

@tool("email_validator")
def validate_email(emails: str) -> str:
    """
    Validate email addresses for deliverability and spam issues using EmailListVerify API.
    
    Args:
        emails: JSON string of email addresses for validation
        
    Example:
        ```json
        {
            "emails": "[\"john@example.com\", \"jane@example.com\"]"
        }
        ```
        
        Or for single email:
        ```json
        {
            "emails": "[\"john.doe@example.com\"]"
        }
        ```
    """
    try:
        if not _email_service.is_api_configured():
            return _email_service.get_api_status_message()
        
        # Parse the emails parameter
        if not emails:
            return "❌ **No Emails Provided**: Please provide emails as a JSON array"
        
        try:
            if isinstance(emails, str):
                email_list = json.loads(emails)
            elif isinstance(emails, list):
                email_list = emails
            else:
                return "❌ **Invalid Input**: 'emails' must be a JSON string or list"
            
            if not isinstance(email_list, list):
                return "❌ **Invalid Format**: 'emails' must be a JSON array of email addresses"
            
        except json.JSONDecodeError:
            return "❌ **Invalid JSON**: Please provide emails as a valid JSON array"
        
        # Clean and validate email list
        clean_emails = []
        for email_addr in email_list:
            if isinstance(email_addr, str) and '@' in email_addr:
                clean_emails.append(email_addr.strip())
        
        if not clean_emails:
            return "❌ **No Valid Emails**: No valid email addresses found in input"
        
        # Perform validation
        if len(clean_emails) == 1:
            # Single email validation
            result = _email_service.validate_single_email(clean_emails[0])
            return _email_service.format_validation_result(clean_emails[0], result)
        else:
            # Bulk email validation
            result = _email_service.validate_bulk_emails(clean_emails)
            return _email_service.format_bulk_validation_result(result)
    
    except Exception as e:
        return f"❌ **Validation Error**: {str(e)}"

 