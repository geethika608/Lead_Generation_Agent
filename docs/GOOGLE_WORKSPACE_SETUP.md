# Google Workspace Integration Setup

This guide will help you set up Google Sheets integration to save data to **your own Google account**. The system now supports **multi-user authentication**, allowing each user to connect their own Google account.

## 🚀 Quick Setup (OAuth2 - Multi-User Authentication)

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the required APIs:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it
   - Search for "Google Drive API" and enable it

### 2. Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" (for local development)
4. Fill in the application name: `Lead Generation Agent`
5. Click "Create"
6. Download the JSON file and rename it to `credentials.json`

### 3. Configure Environment Variables

Add to your `.env` file:
```bash
GOOGLE_CREDENTIALS_FILE=credentials.json
```

### 4. Multi-User Authentication Process

#### How It Works:
- **One `credentials.json` file** - Shared by all users (contains your app's OAuth2 credentials)
- **User-specific token files** - Each user gets their own `tokens/token_XXXXX.pickle` file
- **Session-based authentication** - Each user session is isolated
- **Automatic token management** - Tokens are refreshed automatically

#### For Each User:
1. **First-time setup**: User clicks "Connect Google Account" in the UI
2. **Browser opens**: Google OAuth2 consent screen appears
3. **User signs in**: User signs in with their own Google account
4. **Permissions granted**: User grants access to Sheets and Drive
5. **Token saved**: Authentication token is saved to `tokens/token_XXXXX.pickle`
6. **Future use**: Token is automatically used for subsequent requests

#### User Isolation:
- ✅ **Each user authenticates with their own Google account**
- ✅ **Data is saved to each user's own Google Workspace**
- ✅ **No cross-user data access**
- ✅ **Secure token storage per user**

## 📊 What Gets Saved

### Google Sheets (Per User)
- **Leads Sheet**: Contains all scraped leads with columns:
  - Name
  - Email
  - Company
  - Title
  - LinkedIn URL
  - Source
  - Quality Score

## 🔧 Testing the Integration

### Test Google Sheets
```python
from tools.google_sheets import save_to_google_sheets

# Test data
test_leads = [
    {
        "name": "John Doe",
        "email": "john.doe@company.com",
        "company": "Tech Corp",
        "title": "CTO"
    }
]

result = save_to_google_sheets(test_leads)
print(result)
```

## 🔐 Multi-User Authentication Features

### UI Features:
1. **🔐 Connect Google Account** - Authenticate with your Google account
2. **📊 Check Status** - Check current authentication status
3. **🚫 Revoke Access** - Remove authentication and tokens

### Session Management:
- **Automatic session creation** - Each user gets a unique session ID
- **Token persistence** - Tokens are saved and reused automatically
- **Token refresh** - Expired tokens are automatically refreshed
- **Secure storage** - Tokens are stored in `tokens/` directory

### User Experience:
- **One-time setup** - Users only need to authenticate once
- **Automatic token refresh** - No manual intervention required
- **Secure by default** - Each user's data is isolated
- **Easy revocation** - Users can revoke access anytime

## 🚨 Troubleshooting

### Common Issues:

#### 1. "Google Authentication Required" Error
**Problem**: User hasn't authenticated with Google
**Solution**: 
1. Click "Connect Google Account" in the UI
2. Sign in to your Google account
3. Grant the requested permissions
4. Try the operation again

#### 2. "Invalid Credentials" Error
**Problem**: OAuth2 credentials are invalid or expired
**Solution**:
1. Check that `credentials.json` exists and is valid
2. Ensure the file contains valid OAuth2 client credentials
3. Verify the credentials are for a desktop application

#### 3. "API Not Enabled" Error
**Problem**: Required Google APIs are not enabled
**Solution**:
1. Go to Google Cloud Console and enable the Google Sheets API and Google Drive API
2. Wait a few minutes for the changes to propagate
3. Try the operation again

#### 4. "Quota Exceeded" Error
**Problem**: API quota limits have been reached
**Solution**:
1. Check your Google Cloud Console quotas
2. Consider upgrading your Google Cloud project
3. Wait for quota reset (usually daily)

### API Quotas (Default Limits):
- **Google Sheets API**: 300 requests per minute per project
- **Google Drive API**: 1000 requests per 100 seconds per user

## 🔒 Security Best Practices

### For Users:
1. **Use your own Google account** - Never share credentials
2. **Review permissions** - Only grant necessary permissions
3. **Revoke access when done** - Remove tokens when no longer needed
4. **Monitor activity** - Check Google account activity regularly

### For Developers:
1. **Secure credential storage** - Keep `credentials.json` secure
2. **Token encryption** - Consider encrypting stored tokens
3. **Regular audits** - Monitor API usage and access patterns
4. **User education** - Inform users about security best practices

## 📚 Additional Resources

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/) 