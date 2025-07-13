"""
Tab management for the Gradio interface
"""

import gradio as gr
from typing import Tuple
from .auth_components import AuthComponents
from .profile_components import ProfileComponents
from .interface_builder import InterfaceBuilder
from .progress_tracking import ProgressTracker
from .workflow_runner import WorkflowRunner
from ...services.session_service import session_service

class TabManager:
    """Manages all tabs in the interface"""
    
    def __init__(self):
        """Initialize tab manager"""
        self.auth_components = AuthComponents()
        self.profile_components = ProfileComponents()
        self.interface_builder = InterfaceBuilder()
        self.progress_tracker = ProgressTracker()
        self.workflow_runner = WorkflowRunner()
    
    def create_tabs(self, auth_state: gr.State, session_id: gr.State, user_info: gr.Markdown, browser_session: gr.BrowserState) -> Tuple[gr.Tabs, gr.Tab, gr.Tab]:
        """Create all tabs with proper authentication state handling"""
        
        with gr.Tabs() as main_tabs:
            # Login Tab - Always visible
            with gr.Tab("🔐 Login", id=0, visible=True):
                self._create_login_tab(auth_state, session_id, main_tabs, browser_session)
            
            # Registration Tab - Always visible
            with gr.Tab("📝 Register", id=1, visible=True):
                self._create_registration_tab(auth_state, session_id, main_tabs)
            
            # Main App Tab - Hidden initially, shown when authenticated
            with gr.Tab("🚀 Lead Generation", id=2, visible=False) as main_app_tab:
                self._create_main_app_tab(auth_state, session_id, main_tabs, user_info)
            
            # Profile Tab - Hidden initially, shown when authenticated
            with gr.Tab("👤 Profile", id=3, visible=False) as profile_tab:
                self._create_profile_tab(auth_state, session_id, main_tabs, user_info, profile_tab, browser_session)
        
        return main_tabs, main_app_tab, profile_tab
    
    def _create_login_tab(self, auth_state: gr.State, session_id: gr.State, main_tabs: gr.Tabs, browser_session: gr.BrowserState):
        """Create login tab using AuthComponents with BrowserState"""
        # Get components from AuthComponents
        username_input, password_input, remember_me, login_btn, login_status = self.auth_components.create_login_tab()
        
        # Set up event handlers using AuthComponents handlers with BrowserState
        login_btn.click(
            fn=self.auth_components._handle_login,
            inputs=[username_input, password_input, remember_me, browser_session],
            outputs=[auth_state, session_id, login_status, browser_session]
        )
    
    def _create_registration_tab(self, auth_state: gr.State, session_id: gr.State, main_tabs: gr.Tabs):
        """Create registration tab using AuthComponents"""
        # Get components from AuthComponents
        (username_input, email_input, password_input, confirm_password_input,
         first_name_input, last_name_input, company_input, register_btn, registration_status) = self.auth_components.create_registration_tab()
        
        # Set up event handlers using AuthComponents handlers
        register_btn.click(
            fn=self.auth_components._handle_registration,
            inputs=[
                username_input, email_input, password_input, confirm_password_input,
                first_name_input, last_name_input, company_input
            ],
            outputs=[registration_status]
        )
    
    def _create_main_app_tab(self, auth_state: gr.State, session_id: gr.State, main_tabs: gr.Tabs, user_info: gr.Markdown):
        """Create main application tab with proper component integration"""
        with gr.Column(elem_classes=["main-container"]):
            # Header with user info
            with gr.Row():
                with gr.Column(scale=3):
                    gr.Markdown("# 🚀 Lead Generation Agent")
                    # Display the user info component
                    user_info
            
            # Main application content with proper integration
            with gr.Row():
                # Left column - Input section
                with gr.Column(scale=1):
                    input_components = self.interface_builder.create_input_section()
                    search_strategy, target_clients, campaign_agenda, max_leads, search_depth, run_button = input_components
                
                # Right column - Progress and Results (hidden initially)
                with gr.Column(scale=1, visible=False) as results_column:
                    # Progress section
                    progress_display = self.progress_tracker.create_progress_section()
                    
                    # Workflow results section
                    workflow_output = self.workflow_runner.create_workflow_section()
            
            # Set up event handlers for workflow execution
            def run_workflow(session_id_val, search_strategy_val, target_clients_val, campaign_agenda_val, max_leads_val, search_depth_val):
                """Wrapper function to run workflow with Google auth validation and button state management"""
                # Validate Google authentication before running workflow
                if not session_service.is_google_authenticated(session_id_val):
                    return gr.update(visible=True), gr.update(interactive=True), "❗ **Google Authentication Required**\n\nPlease go to your **Profile tab** and connect your Google account before running lead generation.\n\n**Steps to connect:**\n1. Go to the **👤 Profile** tab\n2. Click **'Connect Google Account'**\n3. Follow the authentication process\n4. Return here and try again"
                
                try:
                    # Disable button and show progress
                    yield gr.update(visible=True), gr.update(interactive=False), "🔄 **Starting Lead Generation Workflow...**\n\nPlease wait while the system processes your request."
                    
                    # Run workflow with session_id
                    result = self.workflow_runner.run_lead_generation(
                        search_strategy_val, target_clients_val, campaign_agenda_val, max_leads_val, search_depth_val, session_id_val
                    )
                    
                    # Re-enable button and show results
                    yield gr.update(visible=True), gr.update(interactive=True), result
                    
                except Exception as e:
                    # Re-enable button and show error
                    yield gr.update(visible=True), gr.update(interactive=True), f"❌ **Error running workflow**: {str(e)}"
            
            run_button.click(
                fn=run_workflow,
                inputs=[session_id, search_strategy, target_clients, campaign_agenda, max_leads, search_depth],
                outputs=[results_column, run_button, workflow_output]
            )
    
    def _create_profile_tab(self, auth_state: gr.State, session_id: gr.State, main_tabs: gr.Tabs, user_info: gr.Markdown, profile_tab: gr.Tab, browser_session: gr.BrowserState):
        """Create profile tab using ProfileComponents with BrowserState"""
        # Get components from ProfileComponents
        (profile_username, profile_email, profile_first_name, profile_last_name, profile_company,
         profile_role, profile_status, profile_created, profile_last_login, update_profile_btn, profile_status_msg,
         google_status, google_email_display, google_auth_btn, google_revoke_btn, google_auth_status,
         current_password, new_password, confirm_new_password, change_password_btn, password_status, logout_btn) = self.profile_components.create_profile_tab()
        
        # Set up event handlers using ProfileComponents handlers
        update_profile_btn.click(
            fn=self.profile_components._handle_profile_update,
            inputs=[session_id, profile_first_name, profile_last_name, profile_company],
            outputs=[profile_status_msg]
        )
        
        # Load profile data when profile tab is accessed
        def load_profile_on_tab_access(session_id_val):
            """Load profile data when profile tab is accessed"""
            if not session_id_val:
                return "", "", "", "", "", "", "", "", ""
            
            try:
                # Get user info from session
                user_data = self.auth_components.get_user_info(session_id_val)
                if not user_data:
                    return "", "", "", "", "", "", "", "", ""
                
                # Get user ID and fetch complete profile from database
                user_id = session_service.get_user_id(session_id_val)
                if not user_id:
                    return "", "", "", "", "", "", "", "", ""
                
                # Get complete user profile from database
                profile = self.profile_components.user_service.get_user_profile(user_id)
                if not profile:
                    # Fallback to session data
                    return (
                        user_data.get("username", ""),
                        user_data.get("email", ""),
                        "",  # first_name
                        "",  # last_name
                        "",  # company
                        user_data.get("role", ""),
                        "Active",  # status
                        "Member since registration",  # created
                        "Last login info"  # last_login
                    )
                
                # Return complete profile data
                return (
                    profile.username or "",
                    profile.email or "",
                    profile.first_name or "",
                    profile.last_name or "",
                    profile.company or "",
                    profile.role.value if profile.role else "",
                    profile.status.value if profile.status else "Active",
                    profile.created_at.strftime('%B %d, %Y') if profile.created_at else "Member since registration",
                    profile.last_login.strftime('%B %d, %Y at %I:%M %p') if profile.last_login else "Last login info"
                )
            
            except Exception as e:
                print(f"Error loading profile data: {e}")
                return "", "", "", "", "", "", "", "", ""
        
        # Load profile data when profile tab is selected
        profile_tab.select(
            fn=load_profile_on_tab_access,
            inputs=[session_id],
            outputs=[
                profile_username, profile_email, profile_first_name, profile_last_name, profile_company,
                profile_role, profile_status, profile_created, profile_last_login
            ]
        )
        
        # Refresh Google status when profile tab is accessed
        def refresh_google_on_tab_access(session_id_val):
            """Refresh Google auth status when profile tab is accessed"""
            if not session_id_val:
                return "**Status:** Not connected", "", False, True
            
            return self.profile_components.refresh_google_status(session_id_val)
        
        # Refresh Google status when profile tab is selected
        profile_tab.select(
            fn=refresh_google_on_tab_access,
            inputs=[session_id],
            outputs=[google_status, google_email_display, google_revoke_btn, google_auth_btn]
        )
        
        # Handle Google authentication with auto-refresh
        def handle_google_auth_with_refresh(session_id_val):
            """Handle Google auth and auto-refresh status"""
            status_msg, should_refresh = self.profile_components._handle_google_auth(session_id_val)
            
            if should_refresh:
                # Auto-refresh the Google status after successful authentication
                status_text, email_display, show_revoke, show_connect = self.profile_components.refresh_google_status(session_id_val)
                return status_msg, status_text, email_display, gr.update(visible=show_revoke), gr.update(visible=show_connect)
            else:
                # Return current status unchanged
                status_text, email_display, show_revoke, show_connect = self.profile_components.refresh_google_status(session_id_val)
                return status_msg, status_text, email_display, gr.update(visible=show_revoke), gr.update(visible=show_connect)
        
        google_auth_btn.click(
            fn=handle_google_auth_with_refresh,
            inputs=[session_id],
            outputs=[google_auth_status, google_status, google_email_display, google_revoke_btn, google_auth_btn]
        )
        
        google_revoke_btn.click(
            fn=self.profile_components._handle_google_revoke,
            inputs=[session_id],
            outputs=[google_auth_status]
        )
        
        change_password_btn.click(
            fn=self.profile_components._handle_password_change,
            inputs=[session_id, current_password, new_password, confirm_new_password],
            outputs=[password_status]
        )
        
        # Logout event handler using AuthComponents with BrowserState
        logout_btn.click(
            fn=self.auth_components._handle_logout,
            inputs=[session_id, browser_session],
            outputs=[auth_state, session_id, user_info, browser_session]
        ) 