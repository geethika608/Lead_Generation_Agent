"""
Authentication UI components for login, registration, and logout
"""

import gradio as gr
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from ...models.user_models import (
    UserLogin, UserRegistration, UserProfile, PasswordChange,
    UserRole, UserStatus
)
from ...services.auth_service import AuthService
from ...services.user_service import UserService
from ...services.session_service import session_service

class AuthComponents:
    """Authentication UI components"""
    
    def __init__(self):
        """Initialize authentication components"""
        self.auth_service = AuthService()
        self.user_service = UserService()
    
    def create_login_tab(self) -> Tuple[gr.Textbox, gr.Textbox, gr.Checkbox, gr.Button, gr.Markdown]:
        """Create login tab components"""
        with gr.Column(elem_classes=["auth-container"]):
            gr.Markdown("# 🔐 Login to Lead Generation Agent")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Welcome Back!")
                    gr.Markdown("Sign in to access your lead generation workspace.")
                
                with gr.Column(scale=1):
                    with gr.Group():
                        username_input = gr.Textbox(
                            label="Username or Email",
                            placeholder="Enter your username or email",
                            scale=2
                        )
                        
                        password_input = gr.Textbox(
                            label="Password",
                            placeholder="Enter your password",
                            type="password",
                            scale=2
                        )
                        
                        remember_me = gr.Checkbox(
                            label="Remember me (30 days)",
                            value=False
                        )
                        
                        login_btn = gr.Button(
                            "Login",
                            variant="primary",
                            size="lg"
                        )
                        
                        login_status = gr.Markdown()
        
        return username_input, password_input, remember_me, login_btn, login_status
    
    def create_registration_tab(self) -> Tuple[gr.Textbox, gr.Textbox, gr.Textbox, gr.Textbox, 
                                              gr.Textbox, gr.Textbox, gr.Textbox, gr.Button, gr.Markdown]:
        """Create registration tab components"""
        with gr.Column(elem_classes=["auth-container"]):
            gr.Markdown("# 📝 Create Your Account")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Join Lead Generation Agent")
                    gr.Markdown("Create your account to start generating leads.")
                
                with gr.Column(scale=1):
                    with gr.Group():
                        
                        username_input = gr.Textbox(
                            label="Username",
                            placeholder="Choose a username (3+ characters, alphanumeric only)",
                            scale=2
                        )
                        
                        email_input = gr.Textbox(
                            label="Email Address",
                            placeholder="Enter your email address",
                            scale=2
                        )
                        
                        password_input = gr.Textbox(
                            label="Password",
                            placeholder="Enter a strong password (8+ characters)",
                            type="password",
                            scale=2
                        )
                        
                        confirm_password_input = gr.Textbox(
                            label="Confirm Password",
                            placeholder="Confirm your password",
                            type="password",
                            scale=2
                        )
                        
                        with gr.Row():
                            first_name_input = gr.Textbox(
                                label="First Name",
                                placeholder="Your first name",
                                scale=1
                            )
                            last_name_input = gr.Textbox(
                                label="Last Name",
                                placeholder="Your last name",
                                scale=1
                            )
                        
                        company_input = gr.Textbox(
                            label="Company",
                            placeholder="Your company name (optional)",
                            scale=2
                        )
                        
                        register_btn = gr.Button(
                            "Create Account",
                            variant="primary",
                            size="lg"
                        )
                        
                        registration_status = gr.Markdown()
        
        return (username_input, email_input, password_input, confirm_password_input,
                first_name_input, last_name_input, company_input, register_btn, registration_status)
    
    def _handle_login(self, username: str, password: str, remember_me: bool, browser_session: list) -> Tuple[bool, str, str, list]:
        """Handle user login with BrowserState persistence"""
        try:
            # Validate credentials
            if not username or not password:
                return False, "", "❌ **Login Failed**\n\nPlease enter both username and password.", browser_session
            
            # Attempt login
            session_id = self.auth_service.login(username, password)
            
            if session_id:
                # Update browser session for persistence - using list structure
                updated_browser_session = [session_id, True, username]
                
                return True, session_id, "✅ **Login Successful!**\n\nWelcome back! You can now access the Lead Generation features.", updated_browser_session
            else:
                return False, "", "❌ **Login Failed**\n\nInvalid username or password. Please try again.", browser_session
                
        except Exception as e:
            print(f"Login error: {e}")
            return False, "", f"❌ **Login Error**\n\nAn error occurred during login: {str(e)}", browser_session
    
    def _handle_registration(self, username: str, email: str, password: str, 
                           confirm_password: str, first_name: str, last_name: str, 
                           company: str) -> str:
        """Handle user registration"""
        try:
            if password != confirm_password:
                return "❌ **Registration failed:** Passwords do not match"
            
            registration_data = UserRegistration(
                username=username,
                email=email,
                password=password,
                first_name=first_name if first_name else None,
                last_name=last_name if last_name else None,
                company=company if company else None
            )
            
            user_account = self.user_service.register_user(registration_data)
            
            return f"✅ **Registration successful!** Welcome, {user_account.username}! You can now login."
        
        except ValueError as e:
            return f"❌ **Registration failed:** {str(e)}"
        except Exception as e:
            return f"❌ **Error:** An unexpected error occurred: {str(e)}"
    
    def _handle_logout(self, session_id: str, browser_session: list) -> Tuple[bool, str, str, list]:
        """Handle user logout with BrowserState cleanup"""
        try:
            # Clear session
            if session_id:
                self.auth_service.logout(session_id)
            
            # Clear browser session - using list structure
            cleared_browser_session = ["", False, ""]
            
            return False, "", "✅ **Logout Successful**\n\nYou have been logged out successfully.", cleared_browser_session
            
        except Exception as e:
            print(f"Logout error: {e}")
            return False, "", f"❌ **Logout Error**\n\nAn error occurred during logout: {str(e)}", browser_session
    
    def get_user_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from session"""
        if not session_id:
            return None
        
        session = session_service.get_session(session_id)
        if not session:
            return None
        
        return {
            "user_id": session.get("user_id"),
            "username": session.get("username"),
            "email": session.get("email"),
            "role": session.get("role"),
            "google_authenticated": session.get("google_authenticated", False),
            "google_email": session.get("google_email")
        }
    
    def is_authenticated(self, session_id: str) -> bool:
        """Check if user is authenticated"""
        return session_service.is_valid_session(session_id)
    
    def validate_and_restore_session(self, session_id: str) -> Tuple[bool, str, str]:
        """Validate and restore session from localStorage"""
        try:
            if not session_id:
                print("Session restoration: No session ID provided")
                return False, "", ""
            
            print(f"Session restoration: Validating session {session_id[:10]}...")
            
            # Check if session is valid
            if not session_service.is_valid_session(session_id):
                print(f"Session restoration: Session {session_id[:10]} is not valid")
                return False, "", ""
            
            # Get session data
            session_data = session_service.get_session(session_id)
            if not session_data:
                print(f"Session restoration: No session data found for {session_id[:10]}")
                return False, "", ""
            
            print(f"Session restoration: Successfully restored session for {session_data.get('username', 'unknown')}")
            
            # Return session info for restoration
            return True, session_id, f"✅ **Session restored!** Welcome back, {session_data['username']}!"
        
        except Exception as e:
            print(f"Session restoration error: {e}")
            return False, "", f"❌ **Session restoration failed:** {str(e)}" 

    def restore_session_from_browser(self, browser_session_data: list) -> Tuple[bool, str, str]:
        """Restore session from BrowserState data"""
        try:
            if not browser_session_data or len(browser_session_data) < 3:
                return False, "", "No session data found"
            
            session_id = browser_session_data[0] if browser_session_data[0] else ""
            auth_state = browser_session_data[1] if len(browser_session_data) > 1 else False
            username = browser_session_data[2] if len(browser_session_data) > 2 else ""
            
            if not session_id or not auth_state:
                return False, "", "No valid session found"
            
            # Validate session
            if self.auth_service.validate_session(session_id):
                # Get user info for welcome message
                user_data = self.get_user_info(session_id)
                if user_data and user_data.get('username'):
                    welcome_msg = f"👋 **Welcome back, {user_data['username']}!**\n\nSession restored successfully."
                else:
                    welcome_msg = "👋 **Welcome back!**\n\nSession restored successfully."
                
                return True, session_id, welcome_msg
            else:
                return False, "", "Session expired or invalid"
                
        except Exception as e:
            print(f"Session restoration error: {e}")
            return False, "", f"Error restoring session: {str(e)}" 