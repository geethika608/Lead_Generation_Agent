#!/usr/bin/env python3
"""
Script to clear existing Google tokens and test authentication
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lead_generation_agent.services.google_auth import GoogleAuthManager

def main():
    """Clear all Google tokens and test authentication"""
    print("🔧 Clearing existing Google tokens...")
    
    # Create GoogleAuthManager instance
    auth_manager = GoogleAuthManager()
    
    # Clear all tokens
    success = auth_manager.clear_all_tokens()
    
    if success:
        print("✅ Successfully cleared all Google tokens")
        print("🔄 Users will need to re-authenticate with Google")
        print("📝 The new authentication will use the updated scopes including 'openid'")
    else:
        print("❌ Failed to clear Google tokens")
        return 1
    
    print("\n🎯 Next steps:")
    print("1. Restart the application")
    print("2. Go to the Profile tab")
    print("3. Click 'Connect Google Account'")
    print("4. Complete the OAuth2 flow")
    print("5. The authentication should now work without scope errors")
    
    return 0

if __name__ == "__main__":
    exit(main()) 