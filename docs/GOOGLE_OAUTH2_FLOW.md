# Google OAuth2 Flow Documentation

## 🔄 Simplified Automatic OAuth2 Flow

Our system uses a **simplified automatic OAuth2 flow** that handles everything automatically without manual URL handling.

### **How It Works:**

```python
# Single method call handles everything
auth_manager = GoogleAuthManager("user123")
success = auth_manager.authenticate_user("user123")
```

**Process:**
1. `authenticate_user()` checks for existing tokens in database
2. If no valid tokens, opens browser automatically
3. User signs in to Google and grants permissions
4. Google redirects to local server (e.g., `http://localhost:8080`)
5. Local server automatically exchanges authorization code for tokens
6. Tokens saved to database securely

## 🎯 How Authentication Works

### **Google Does NOT Call Our Methods Directly**

The OAuth2 flow is handled automatically by the Google OAuth library:

1. **Our Application** → Calls `authenticate_user()`
2. **Google OAuth Library** → Opens browser → Handles redirect → Exchanges code for tokens
3. **Our Application** → Receives tokens → Saves to database

### **Example Implementation:**

#### **In the UI (Gradio Interface):**
```python
# The UI uses the automatic flow
def handle_google_auth():
    if self.current_session:
        # This opens browser automatically and handles everything
        success = self.auth_service.authenticate_google_user(self.current_session.user_id)
        return "Authentication successful!" if success else "Authentication failed!"
```

#### **In Google Sheets Tools:**
```python
# Tools use the automatic flow when credentials are missing
def _initialize_service(self):
    credentials = self.auth_manager.get_credentials()
    if not credentials:
        # This triggers automatic authentication
        self.auth_manager.authenticate_user(self.user_id)
        credentials = self.auth_manager.get_credentials()
```

## 🚀 Setting Up Google OAuth2

### **1. Google Cloud Console Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API, Google Drive API
4. Go to "APIs & Services" > "Credentials"
5. Create OAuth2 Client ID for "Desktop application"
6. Download credentials as `credentials.json`

### **2. Environment Configuration:**
```bash
# Add to your .env file
GOOGLE_CREDENTIALS_FILE=credentials.json
```

### **3. Required Scopes:**
```python
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]
```

## 🔐 Multi-User Authentication

### **How It Works:**
- **One `credentials.json`** - Shared by all users (app credentials)
- **User-specific tokens** - Each user gets their own token file
- **Automatic isolation** - No cross-user data access
- **Secure storage** - Tokens stored in `tokens/` directory

### **User Flow:**
1. **First visit** - User clicks "Connect Google Account"
2. **Browser opens** - Google OAuth2 consent screen
3. **User signs in** - With their own Google account
4. **Permissions granted** - Access to Sheets and Drive
5. **Token saved** - To `tokens/token_XXXXX.pickle`
6. **Future visits** - Token automatically used

## 🛠️ Implementation Details

### **Token Storage:**
```python
# Tokens are stored per user
token_file = f"tokens/token_{user_id}.pickle"

# Automatic token refresh
if credentials.expired and credentials.refresh_token:
    credentials.refresh(Request())
    save_credentials(credentials, token_file)
```

### **Error Handling:**
```python
try:
    credentials = get_credentials(user_id)
    if not credentials:
        # Trigger authentication flow
        authenticate_user(user_id)
        credentials = get_credentials(user_id)
except Exception as e:
    logger.error(f"Authentication failed: {e}")
    return False
```

## 🔒 Security Considerations

### **Token Security:**
- Tokens are stored locally in `tokens/` directory
- Each user has their own isolated token file
- Tokens are automatically refreshed when expired
- Users can revoke access anytime

### **Data Isolation:**
- Each user's data is saved to their own Google account
- No cross-user data access is possible
- API calls are made with user-specific credentials

## 🚨 Troubleshooting

### **Common Issues:**

1. **"Credentials file not found"**
   - Check that `credentials.json` exists
   - Verify the file path in `.env`

2. **"Authentication failed"**
   - Delete user's token file: `tokens/token_XXXXX.pickle`
   - Ensure user is using correct Google account
   - Check OAuth2 client configuration

3. **"API not enabled"**
   - Enable Google Sheets API and Google Drive API
   - Wait for changes to propagate

4. **"Permission denied"**
   - Ensure user granted all requested permissions
   - Check Google account has access to Google Workspace

## 📚 Additional Resources

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Google Drive API](https://developers.google.com/drive/api) 