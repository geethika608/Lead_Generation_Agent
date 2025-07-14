"""
Main Gradio interface for the Lead Generation Agent
"""

import gradio as gr
from dotenv import load_dotenv

from .components.session_manager import SessionManager
from .components.tab_manager import TabManager

# Load environment variables
load_dotenv()

class LeadGenerationInterface:
    """Main interface for the Lead Generation Agent"""
    
    def __init__(self):
        """Initialize the interface"""
        self.session_manager = SessionManager()
        self.tab_manager = TabManager()
    
    def create_interface(self) -> gr.Blocks:
        """Create the main interface with authentication"""
        with gr.Blocks(
            title="Lead Generation Agent",
            theme=gr.themes.Soft(),
            css="""
            /* Global font settings */
            * {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
            }
            
            .auth-container { 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px; 
            }
            .main-container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px; 
            }
            .hidden-tab {
                display: none !important;
            }
            .tab-transition {
                transition: opacity 0.3s ease-in-out;
            }
            .welcome-message {
                font-size: 1.2em;
                color: #2c3e50;
                margin-bottom: 10px;
                font-weight: 500;
            }
            .status-message {
                background-color: #e8f5e8;
                border: 1px solid #4caf50;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
                text-align: center;
            }

            
            /* Google authentication styling */
            .google-auth-success {
                background-color: #e8f5e8;
                border: 1px solid #4caf50;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
            }
            
            .google-auth-info {
                background-color: #e3f2fd;
                border: 1px solid #2196f3;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
            }
            """,

        ) as interface:
            
            # Create session components with BrowserState
            auth_state, session_id, user_info, session_id_input, restore_btn, browser_session = self.session_manager.create_session_components()
            
            # Create tabs with BrowserState
            main_tabs, main_app_tab, profile_tab = self.tab_manager.create_tabs(auth_state, session_id, user_info, browser_session)
            
            # Set up session restoration from BrowserState
            def restore_session_on_load(browser_session_data):
                """Restore session from BrowserState on page load"""
                if browser_session_data and len(browser_session_data) >= 3 and browser_session_data[0]:
                    return self.tab_manager.auth_components.restore_session_from_browser(browser_session_data)
                return False, "", ""
            
            # Load and restore session from BrowserState
            interface.load(
                fn=restore_session_on_load,
                inputs=[browser_session],
                outputs=[auth_state, session_id, user_info]
            )
            
            # Set up authentication state handlers
            self.session_manager.setup_auth_state_handlers(
                auth_state, session_id, main_tabs, main_app_tab, profile_tab, user_info,
                self.tab_manager.auth_components
            )
        
        return interface


def create_interface():
    """Create and return the main interface"""
    interface = LeadGenerationInterface()
    return interface.create_interface()


if __name__ == "__main__":
    # Launch the interface
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    ) 