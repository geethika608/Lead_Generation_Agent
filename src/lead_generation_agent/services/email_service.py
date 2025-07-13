"""
Email service for validation and spam detection
"""

import requests
import os
import time
import json
from typing import List, Dict, Optional, Union
from ..models.lead_models import ValidatedLeads, Lead

class EmailService:
    """Service for email validation and spam detection"""
    
    def __init__(self):
        self.api_key = os.getenv('EMAILLISTVERIFY_API_KEY')
        self.base_url = "https://apps.emaillistverify.com/api/verifyEmail"
    
    def validate_single_email(self, email: str) -> Dict:
        """Validate a single email address using EmailListVerify API"""
        try:
            if not self.api_key:
                return {
                    'email': email,
                    'error': 'EmailListVerify API key not configured',
                    'is_valid': False
                }
            
            params = {
                'secret': self.api_key,
                'email': email
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Map API response to our format
            validation_result = {
                'email': email,
                'is_valid': result.get('status') == 'success',
                'deliverability': result.get('deliverability', 'unknown'),
                'is_spam_trap': result.get('spam_trap', False),
                'is_disposable': result.get('disposable', False),
                'is_catch_all': result.get('catch_all', False),
                'has_syntax_error': result.get('syntax_error', False),
                'score': result.get('score', 0),
                'details': result
            }
            
            return validation_result
            
        except Exception as e:
            return {
                'email': email,
                'error': f"Validation failed: {str(e)}",
                'is_valid': False
            }
    
    def validate_bulk_emails(self, emails: List[str]) -> Dict:
        """Validate multiple email addresses"""
        results = []
        valid_emails = []
        invalid_emails = []
        spam_traps = []
        disposable_emails = []
        catch_all_domains = []
        
        for email in emails:
            result = self.validate_single_email(email)
            results.append(result)
            
            if result.get('is_valid', False):
                valid_emails.append(email)
            else:
                invalid_emails.append(email)
            
            # Track specific issues
            if result.get('is_spam_trap', False):
                spam_traps.append(email)
            if result.get('is_disposable', False):
                disposable_emails.append(email)
            if result.get('is_catch_all', False):
                catch_all_domains.append(email)
            
            # Add delay to respect API rate limits
            time.sleep(0.1)
        
        return {
            'total_emails': len(emails),
            'valid_emails': valid_emails,
            'invalid_emails': invalid_emails,
            'spam_traps': spam_traps,
            'disposable_emails': disposable_emails,
            'catch_all_domains': catch_all_domains,
            'validation_rate': len(valid_emails) / len(emails) if emails else 0,
            'detailed_results': results
        }
    
    def validate_leads(self, leads: List[Lead]) -> ValidatedLeads:
        """Validate email addresses for a list of leads"""
        emails = [lead.email for lead in leads if lead.email]
        
        if not emails:
            return ValidatedLeads(
                leads=leads,
                validation_results=[],
                valid_count=0,
                invalid_count=0,
                total_count=0
            )
        
        validation_result = self.validate_bulk_emails(emails)
        
        # Update leads with validation status
        validated_leads = []
        for lead in leads:
            if lead.email:
                # Find validation result for this email
                email_validation = next(
                    (r for r in validation_result['detailed_results'] if r['email'] == lead.email),
                    None
                )
                if email_validation:
                    # Update lead with validation info
                    lead_dict = lead.dict()
                    lead_dict['email_valid'] = email_validation.get('is_valid', False)
                    lead_dict['email_score'] = email_validation.get('score', 0)
                    lead_dict['is_spam_trap'] = email_validation.get('is_spam_trap', False)
                    lead_dict['is_disposable'] = email_validation.get('is_disposable', False)
                    lead_dict['is_catch_all'] = email_validation.get('is_catch_all', False)
                    validated_leads.append(Lead(**lead_dict))
                else:
                    validated_leads.append(lead)
            else:
                validated_leads.append(lead)
        
        return ValidatedLeads(
            leads=validated_leads,
            validation_results=validation_result['detailed_results'],
            valid_count=len(validation_result['valid_emails']),
            invalid_count=len(validation_result['invalid_emails']),
            total_count=validation_result['total_emails']
        )
    
    def format_validation_result(self, email: str, result: Dict) -> str:
        """Format validation result for display"""
        if result.get('error'):
            return f"❌ **Validation Error**: {result['error']}"
        
        # Format the result
        status = "✅ Valid" if result['is_valid'] else "❌ Invalid"
        spam_trap = "🚨 SPAM TRAP" if result['is_spam_trap'] else "✅ Clean"
        disposable = "📧 Disposable" if result['is_disposable'] else "✅ Professional"
        catch_all = "🎯 Catch-all" if result['is_catch_all'] else "✅ Specific"
        
        return f"""📧 **Email Validation Result**

**Email**: {email}
**Status**: {status}
**Deliverability**: {result['deliverability']}
**Spam Trap**: {spam_trap}
**Disposable**: {disposable}
**Catch-all**: {catch_all}
**Score**: {result['score']}/100

**Recommendation**: {'✅ Safe to use' if result['is_valid'] and not result['is_spam_trap'] else '⚠️ Review before use'}"""
    
    def format_bulk_validation_result(self, result: Dict) -> str:
        """Format bulk validation result for display"""
        return f"""📧 **Bulk Email Validation Results**

**Total Emails**: {result['total_emails']}
**Valid Emails**: {len(result['valid_emails'])} ({result['validation_rate']:.1%})
**Invalid Emails**: {len(result['invalid_emails'])}
**Spam Traps**: {len(result['spam_traps'])}
**Disposable Emails**: {len(result['disposable_emails'])}
**Catch-all Domains**: {len(result['catch_all_domains'])}

**Valid Emails**: {', '.join(result['valid_emails'][:5])}{'...' if len(result['valid_emails']) > 5 else ''}
**Spam Traps**: {', '.join(result['spam_traps'][:3])}{'...' if len(result['spam_traps']) > 3 else ''}

**Recommendation**: {'✅ List is clean' if len(result['spam_traps']) == 0 else '⚠️ Remove spam traps to protect sender reputation'}"""
    
    def is_api_configured(self) -> bool:
        """Check if EmailListVerify API is configured"""
        return bool(self.api_key)
    
    def get_api_status_message(self) -> str:
        """Get API configuration status message"""
        if not self.is_api_configured():
            return "❌ **EmailListVerify API Key Required**\n\nPlease set EMAILLISTVERIFY_API_KEY in your environment variables.\n\n**What you need to do**:\n1. Sign up at https://www.emaillistverify.com/\n2. Get your API key from the dashboard\n3. Add EMAILLISTVERIFY_API_KEY=your_key to your .env file"
        return "✅ EmailListVerify API configured" 