"""
Session management and authentication state handling for the Gradio interface
"""

import gradio as gr
from typing import Tuple
from ...services.session_service import session_service

class SessionManager:
    """Manages session persistence and authentication state"""
    
    def __init__(self):
        """Initialize session manager"""
        pass
    
    def create_session_components(self) -> Tuple[gr.State, gr.State, gr.Markdown, gr.Textbox, gr.Button, gr.BrowserState]:
        """Create session-related components"""
        # Authentication state
        auth_state = gr.State(False)  # False = not authenticated, True = authenticated
        session_id = gr.State("")     # Store session ID
        
        # Browser state for localStorage persistence - using simple list structure
        browser_session = gr.BrowserState(["", False, ""])  # [session_id, auth_state, username]
        
        # User info component
        user_info = gr.Markdown("Welcome!", elem_classes=["welcome-message"])
        
        # Hidden textbox to store session ID from JavaScript
        session_id_input = gr.Textbox(visible=False, elem_id="session_id_input")
        
        # Session restoration button (hidden, triggered by JavaScript)
        restore_btn = gr.Button("Restore Session", visible=False, elem_id="restore_session_btn")
        
        return auth_state, session_id, user_info, session_id_input, restore_btn, browser_session
    
    def setup_auth_state_handlers(self, auth_state: gr.State, session_id: gr.State, 
                                main_tabs: gr.Tabs, main_app_tab: gr.Tab, profile_tab: gr.Tab, 
                                user_info: gr.Markdown, auth_components):
        """Set up handlers for authentication state changes"""
        
        def update_tab_visibility_and_user_info(auth_state_val, session_id_val):
            """Update tab visibility and user info based on authentication state"""
            if auth_state_val and session_id_val:
                # Get user info for welcome message
                user_data = auth_components.get_user_info(session_id_val)
                if user_data and user_data.get('username'):
                    welcome_msg = f"👋 **Welcome, {user_data['username']}!**"
                else:
                    welcome_msg = "👋 **Welcome!**"
                
                return (
                    gr.update(visible=False),  # Login tab
                    gr.update(visible=False),  # Register tab  
                    gr.update(visible=True),   # Main app tab
                    gr.update(visible=True),   # Profile tab
                    welcome_msg                # User info display
                )
            else:
                return (
                    gr.update(visible=True),   # Login tab
                    gr.update(visible=True),   # Register tab
                    gr.update(visible=False),  # Main app tab
                    gr.update(visible=False),  # Profile tab
                    "Welcome! Please login to continue."  # User info display
                )
        
        # Update tab visibility when auth state changes
        auth_state.change(
            fn=update_tab_visibility_and_user_info,
            inputs=[auth_state, session_id],
            outputs=[
                main_tabs.children[0],  # Login tab
                main_tabs.children[1],  # Register tab
                main_tabs.children[2],  # Main app tab
                main_tabs.children[3],  # Profile tab
                user_info  # User info display
            ]
        )
        
        # Also update when session_id changes
        session_id.change(
            fn=update_tab_visibility_and_user_info,
            inputs=[auth_state, session_id],
            outputs=[
                main_tabs.children[0],  # Login tab
                main_tabs.children[1],  # Register tab
                main_tabs.children[2],  # Main app tab
                main_tabs.children[3],  # Profile tab
                user_info  # User info display
            ]
        )
        
        # Handle tab switching after login
        def switch_to_main_app_after_login(auth_state_val, session_id_val):
            """Switch to main app tab after successful login"""
            if auth_state_val and session_id_val:
                return gr.update(selected=2)  # Switch to main app tab (index 2)
            return gr.update()
        
        # Switch to main app tab when authenticated
        auth_state.change(
            fn=switch_to_main_app_after_login,
            inputs=[auth_state, session_id],
            outputs=[main_tabs]
        ) 