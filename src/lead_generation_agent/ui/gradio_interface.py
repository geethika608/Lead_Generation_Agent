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
            /* Autocomplete control for registration and profile fields */
            .no-autocomplete input {
                autocomplete: "off" !important;
            }
            .new-password input {
                autocomplete: "new-password" !important;
            }
            .current-password input {
                autocomplete: "current-password" !important;
            }
            .login-field input {
                /* Allow default autocomplete for login fields */
                autocomplete: "on" !important;
            }
            
            /* Ensure login fields work with browser autofill using proper selectors */
            #login_username input {
                autocomplete: "username" !important;
            }
            #login_password input {
                autocomplete: "current-password" !important;
            }
            
            /* Registration field autofill */
            #register_username input {
                autocomplete: "username" !important;
            }
            #register_email input {
                autocomplete: "email" !important;
            }
            #register_password input {
                autocomplete: "new-password" !important;
            }
            #register_confirm_password input {
                autocomplete: "new-password" !important;
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
            js="""
            function() {
                // Force browser autofill detection for login fields
                function triggerAutofill() {
                    console.log('Triggering autofill detection...');
                    
                    // Find login fields
                    const usernameField = document.querySelector('#login_username input');
                    const passwordField = document.querySelector('#login_password input');
                    
                    if (usernameField && passwordField) {
                        console.log('Login fields found, triggering autofill...');
                        
                        // Set proper attributes for login fields
                        usernameField.setAttribute('autocomplete', 'username');
                        usernameField.setAttribute('name', 'username');
                        usernameField.setAttribute('type', 'text');
                        
                        passwordField.setAttribute('autocomplete', 'current-password');
                        passwordField.setAttribute('name', 'password');
                        passwordField.setAttribute('type', 'password');
                        
                        // Create a temporary form to trigger autofill
                        const tempForm = document.createElement('form');
                        tempForm.setAttribute('autocomplete', 'on');
                        tempForm.style.display = 'none';
                        
                        const tempUsername = usernameField.cloneNode(true);
                        const tempPassword = passwordField.cloneNode(true);
                        
                        tempForm.appendChild(tempUsername);
                        tempForm.appendChild(tempPassword);
                        document.body.appendChild(tempForm);
                        
                        // Focus and blur to trigger autofill detection
                        tempUsername.focus();
                        tempUsername.blur();
                        tempPassword.focus();
                        tempPassword.blur();
                        
                        // Remove temporary form
                        setTimeout(() => {
                            document.body.removeChild(tempForm);
                        }, 100);
                        
                        console.log('Autofill detection triggered');
                    } else {
                        console.log('Login fields not found yet, retrying...');
                        // Retry after a short delay
                        setTimeout(triggerAutofill, 500);
                    }
                }
                
                // Trigger autofill detection when page loads
                window.addEventListener('load', function() {
                    setTimeout(triggerAutofill, 1000);
                });
                
                // Also trigger when DOM is ready
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', function() {
                        setTimeout(triggerAutofill, 1000);
                    });
                } else {
                    setTimeout(triggerAutofill, 1000);
                }
                
                // Trigger autofill when switching to login tab
                document.addEventListener('click', function(e) {
                    if (e.target && e.target.textContent && e.target.textContent.includes('Login')) {
                        setTimeout(triggerAutofill, 100);
                    }
                });
                
                // Monitor for tab changes
                const observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.type === 'childList') {
                            // Check if login tab is now visible
                            const loginTab = document.querySelector('[data-testid="tab-0"]');
                            if (loginTab && loginTab.getAttribute('aria-selected') === 'true') {
                                setTimeout(triggerAutofill, 100);
                            }
                        }
                    });
                });
                
                // Start observing
                setTimeout(() => {
                    const tabsContainer = document.querySelector('[data-testid="tabs"]');
                    if (tabsContainer) {
                        observer.observe(tabsContainer, { childList: true, subtree: true });
                    }
                }, 2000);
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