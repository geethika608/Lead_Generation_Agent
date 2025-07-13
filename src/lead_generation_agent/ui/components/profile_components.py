"""
User profile UI components for profile management and Google integration
"""

import gradio as gr
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from ...models.user_models import UserProfile, PasswordChange
from ...services.user_service import UserService
from ...services.google_auth import GoogleAuthManager
from ...services.session_service import session_service

class ProfileComponents:
    """User profile UI components"""
    
    def __init__(self):
        """Initialize profile components"""
        self.user_service = UserService()
        self.google_auth_manager = GoogleAuthManager()
    
    def create_profile_tab(self) -> Tuple[gr.Textbox, gr.Textbox, gr.Textbox, gr.Textbox, gr.Textbox,
                                         gr.Textbox, gr.Textbox, gr.Textbox, gr.Textbox, gr.Button, gr.Markdown,
                                         gr.Markdown, gr.Textbox, gr.Button, gr.Button, gr.Markdown,
                                         gr.Textbox, gr.Textbox, gr.Textbox, gr.Button, gr.Markdown, gr.Button]:
        """Create profile tab components"""
        with gr.Column(elem_classes=["main-container"]):
            gr.Markdown("# 👤 User Profile")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Account Information")
                    
                    with gr.Group():
                        profile_username = gr.Textbox(
                            label="Username",
                            interactive=False
                        )
                        
                        profile_email = gr.Textbox(
                            label="Email",
                            interactive=False
                        )
                        
                        profile_first_name = gr.Textbox(
                            label="First Name",
                            placeholder="Update your first name",
                            elem_id="profile_first_name",
                            elem_classes=["no-autocomplete"]
                        )
                        
                        profile_last_name = gr.Textbox(
                            label="Last Name",
                            placeholder="Update your last name",
                            elem_id="profile_last_name",
                            elem_classes=["no-autocomplete"]
                        )
                        
                        profile_company = gr.Textbox(
                            label="Company",
                            placeholder="Update your company",
                            elem_id="profile_company",
                            elem_classes=["no-autocomplete"]
                        )
                        
                        profile_role = gr.Textbox(
                            label="Role",
                            interactive=False
                        )
                        
                        profile_status = gr.Textbox(
                            label="Status",
                            interactive=False
                        )
                        
                        profile_created = gr.Textbox(
                            label="Member Since",
                            interactive=False
                        )
                        
                        profile_last_login = gr.Textbox(
                            label="Last Login",
                            interactive=False
                        )
                        
                        update_profile_btn = gr.Button(
                            "Update Profile",
                            variant="primary"
                        )
                        
                        profile_status_msg = gr.Markdown()
                
                with gr.Column(scale=1):
                    gr.Markdown("### Google Integration")
                    gr.Markdown("""
                    **Connect your Google account to enable:**
                    - Google Sheets integration for lead data export
                    - Google Docs integration for campaign reports
                    - Email validation and management
                    
                    ⚠️ **Note:** After authentication, you'll need to manually close the Google tab and refresh the status below.
                    """)
                    
                    with gr.Group():
                        google_status = gr.Markdown("**Status:** Not connected")
                        
                        google_email_display = gr.Textbox(
                            label="Google Account",
                            interactive=False,
                            visible=False
                        )
                        
                        with gr.Row():
                            google_auth_btn = gr.Button(
                                "Connect Google Account",
                                variant="secondary"
                            )
                            
                            google_revoke_btn = gr.Button(
                                "Disconnect Google",
                                variant="stop",
                                visible=False
                            )
                        

                        
                        google_auth_status = gr.Markdown()
                    
                    gr.Markdown("### Security")
                    
                    with gr.Group():
                        current_password = gr.Textbox(
                            label="Current Password",
                            type="password",
                            placeholder="Enter current password",
                            elem_id="current_password",
                            elem_classes=["current-password"]
                        )
                        
                        new_password = gr.Textbox(
                            label="New Password",
                            type="password",
                            placeholder="Enter new password",
                            elem_id="new_password",
                            elem_classes=["new-password"]
                        )
                        
                        confirm_new_password = gr.Textbox(
                            label="Confirm New Password",
                            type="password",
                            placeholder="Confirm new password",
                            elem_id="confirm_new_password",
                            elem_classes=["new-password"]
                        )
                        
                        change_password_btn = gr.Button(
                            "Change Password",
                            variant="secondary"
                        )
                        
                        password_status = gr.Markdown()
                    
                    gr.Markdown("### Account Actions")
                    
                    with gr.Group():
                        logout_btn = gr.Button(
                            "Logout",
                            variant="stop",
                            size="lg"
                        )
        
        return (profile_username, profile_email, profile_first_name, profile_last_name, profile_company,
                profile_role, profile_status, profile_created, profile_last_login, update_profile_btn, profile_status_msg,
                google_status, google_email_display, google_auth_btn, google_revoke_btn, google_auth_status,
                current_password, new_password, confirm_new_password, change_password_btn, password_status, logout_btn)
    
    def _handle_profile_update(self, session_id: str, first_name: str, last_name: str, company: str) -> str:
        """Handle profile update"""
        try:
            if not session_service.is_valid_session(session_id):
                return "❌ **Error:** You must be logged in to update your profile"
            
            user_id = session_service.get_user_id(session_id)
            if not user_id:
                return "❌ **Error:** Invalid session"
            
            success = self.user_service.update_user_profile(
                user_id, first_name=first_name, last_name=last_name, company=company
            )
            
            if success:
                return "✅ **Profile updated successfully!**"
            else:
                return "❌ **Error:** Failed to update profile"
        
        except Exception as e:
            return f"❌ **Error:** An unexpected error occurred: {str(e)}"
    
    def _handle_google_auth(self, session_id: str) -> tuple:
        """Handle Google authentication and return status with refresh flag"""
        try:
            if not session_service.is_valid_session(session_id):
                return "❌ **Error:** You must be logged in to authenticate with Google", False
            
            user_id = session_service.get_user_id(session_id)
            if not user_id:
                return "❌ **Error:** Invalid session", False
            
            # Use GoogleAuthManager to authenticate
            success = self.google_auth_manager.authenticate_user(user_id)
            
            if success:
                # Get user profile to get Google email
                profile = self.user_service.get_user_profile(user_id)
                google_email = profile.google_email if profile else ""
                
                # Update user's Google auth status in database
                self.user_service.update_google_auth_status(user_id, True)
                
                # Sync to session table
                session_service.update_google_auth_status(session_id, True, google_email)
                
                return "✅ **Google authentication successful!**", True
            else:
                return "❌ **Error:** Failed to authenticate with Google", False
        
        except Exception as e:
            return f"❌ **Error:** An unexpected error occurred: {str(e)}", False
    
    def _handle_google_revoke(self, session_id: str) -> str:
        """Handle Google authentication revocation"""
        try:
            if not session_service.is_valid_session(session_id):
                return "❌ **Error:** You must be logged in to revoke Google authentication"
            
            user_id = session_service.get_user_id(session_id)
            if not user_id:
                return "❌ **Error:** Invalid session"
            
            # Use GoogleAuthManager to revoke authentication
            success = self.google_auth_manager.revoke_authentication(user_id)
            
            if success:
                # Update user's Google auth status in database
                self.user_service.update_google_auth_status(user_id, False)
                
                # Sync to session table
                session_service.update_google_auth_status(session_id, False, None)
                
                return "✅ **Google authentication revoked successfully!**"
            else:
                return "❌ **Error:** Failed to revoke Google authentication"
        
        except Exception as e:
            return f"❌ **Error:** An unexpected error occurred: {str(e)}"
    
    def _handle_password_change(self, session_id: str, current_password: str, new_password: str, confirm_password: str) -> str:
        """Handle password change"""
        try:
            if not session_service.is_valid_session(session_id):
                return "❌ **Error:** You must be logged in to change your password"
            
            if new_password != confirm_password:
                return "❌ **Error:** New passwords do not match"
            
            user_id = session_service.get_user_id(session_id)
            if not user_id:
                return "❌ **Error:** Invalid session"
            
            success = self.user_service.change_password(
                user_id, current_password, new_password
            )
            
            if success:
                return "✅ **Password changed successfully!**"
            else:
                return "❌ **Error:** Failed to change password. Please check your current password."
        
        except Exception as e:
            return f"❌ **Error:** An unexpected error occurred: {str(e)}"
    
    def _handle_profile_load(self, session_id: str) -> Tuple[str, str, str]:
        """Handle profile loading"""
        try:
            if not session_service.is_valid_session(session_id):
                return "", "", ""
            
            user_id = session_service.get_user_id(session_id)
            if not user_id:
                return "", "", ""
            
            profile = self.user_service.get_user_profile(user_id)
            if not profile:
                return "", "", ""
            
            return (
                profile.first_name or "",
                profile.last_name or "",
                profile.company or ""
            )
        
        except Exception as e:
            print(f"Error loading profile: {e}")
            return "", "", ""
    
    def load_profile_data(self) -> Dict[str, Any]:
        """Load profile data for current user"""
        if not session_service.is_authenticated():
            return {}
        
        try:
            profile = self.user_service.get_user_profile(session_service.get_current_user_id())
            if not profile:
                return {}
            
            return {
                'username': profile.username,
                'email': profile.email,
                'first_name': profile.first_name or '',
                'last_name': profile.last_name or '',
                'company': profile.company or '',
                'role': profile.role.value,
                'status': profile.status.value,
                'created_at': profile.created_at.strftime('%B %d, %Y') if profile.created_at else '',
                'last_login': profile.last_login.strftime('%B %d, %Y at %I:%M %p') if profile.last_login else '',
                'google_authenticated': profile.google_authenticated,
                'google_email': profile.google_email or ''
            }
        except Exception:
            return {}
    
    def refresh_google_status(self, session_id: str) -> tuple:
        """Refresh Google authentication status display"""
        try:
            if not session_service.is_valid_session(session_id):
                return "**Status:** Not connected", "", gr.update(visible=False), gr.update(visible=True)
            
            user_id = session_service.get_user_id(session_id)
            if not user_id:
                return "**Status:** Not connected", "", gr.update(visible=False), gr.update(visible=True)
            
            # Get user profile to get the most up-to-date Google auth status
            profile = self.user_service.get_user_profile(user_id)
            if not profile:
                return "**Status:** Not connected", "", gr.update(visible=False), gr.update(visible=True)
            
            # Check if user is authenticated with Google
            is_authenticated = profile.google_authenticated
            
            # Sync the status to session table
            session_service.update_google_auth_status(session_id, is_authenticated, profile.google_email)
            
            if is_authenticated:
                google_email = profile.google_email if profile.google_email else "Connected to Google"
                
                status_text = "**Status:** ✅ Connected"
                email_display = google_email
                show_revoke = gr.update(visible=True)
                show_connect = gr.update(visible=False)
            else:
                status_text = "**Status:** ❌ Not connected"
                email_display = ""
                show_revoke = gr.update(visible=False)
                show_connect = gr.update(visible=True)
            
            return status_text, email_display, show_revoke, show_connect
        
        except Exception as e:
            return f"**Status:** Error - {str(e)}", "", gr.update(visible=False), gr.update(visible=True)