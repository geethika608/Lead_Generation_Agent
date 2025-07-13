"""
Workflow service for executing lead generation workflows
"""

import logging
import time
import threading
from typing import Dict, Any
from ..workflows.lead_generation_workflow import run_lead_generation_workflow
from .progress_service import ProgressService
from .analytics_service import AnalyticsService
from .email_service import EmailService

# Set up logging
logger = logging.getLogger(__name__)

class WorkflowService:
    """Service for workflow execution and management"""
    
    def __init__(self):
        """Initialize workflow service"""
        self.progress_service = ProgressService()
        self.analytics_service = AnalyticsService()
        self.email_service = EmailService()
    
    def run_lead_generation(self, search_strategy: str, target_clients: str, campaign_agenda: str,
                           max_leads: int, search_depth: int, session_id: str = None, progress_fn=None) -> str:
        """
        Run the lead generation workflow with user inputs, always enabling all features
        
        Args:
            search_strategy: Search strategy for finding leads
            target_clients: Comma-separated list of target roles
            campaign_agenda: Campaign objective
            max_leads: Maximum number of leads to generate
            search_depth: Search depth (1-5)
            session_id: User session ID for authentication
            progress_fn: Optional callback function for progress updates
            
        Returns:
            Formatted string with workflow results
        """
        try:
            # Validate inputs
            user_input = self._validate_inputs(search_strategy, target_clients, campaign_agenda, max_leads, search_depth)
            
            # Always enable all features
            user_input['enable_evaluation'] = True
            user_input['enable_spam_checking'] = True
            
            # Get user authentication data from session
            user_auth = None
            if session_id:
                from .session_service import session_service
                try:
                    logger.info(f"Attempting to get session data for session_id: {session_id}")
                    user_data = session_service.get_session(session_id)
                    logger.info(f"Retrieved session data: {user_data}")
                    if user_data:
                        user_auth = {
                            'user_id': user_data.get('user_id'),
                            'username': user_data.get('username'),
                            'email': user_data.get('email'),
                            'role': user_data.get('role'),
                            'google_authenticated': user_data.get('google_authenticated', False),
                            'google_email': user_data.get('google_email')
                        }
                        logger.info(f"User authentication data retrieved for user: {user_auth['username']}")
                    else:
                        logger.warning(f"No session data found for session_id: {session_id}")
                except Exception as e:
                    logger.warning(f"Failed to get user authentication data: {e}")
            else:
                logger.warning("No session_id provided, cannot retrieve user authentication data")
            
            # Start progress monitoring in a separate thread
            def monitor_progress():
                while True:
                    try:
                        if self.progress_service.is_workflow_completed():
                            break
                        if progress_fn:
                            progress_fn(self.progress_service.get_live_progress())
                        time.sleep(2)  # Update every 2 seconds
                    except Exception as e:
                        logger.error(f"Progress monitoring error: {e}")
                        break
            
            # Start the workflow
            self.progress_service.start_workflow()
            
            # Start progress monitoring
            progress_thread = threading.Thread(target=monitor_progress, daemon=True)
            progress_thread.start()
            
            # Run the workflow with user authentication data
            logger.info(f"Starting workflow with user input: {user_input}")
            logger.info(f"User authentication: {user_auth}")
            result = run_lead_generation_workflow(user_input, user_auth)
            
            # Mark workflow as completed
            success = result['status'] == 'success'
            self.progress_service.complete_workflow(success)
            
            # Get final state
            final_state = self.progress_service.get_workflow_status()
            
            if success:
                return self._format_success_result(user_input, result, final_state)
            else:
                return self._format_error_result(result)
                
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            self.progress_service.complete_workflow(False)
            return self._format_exception_result(str(e))
    
    def _validate_inputs(self, search_strategy: str, target_clients: str, campaign_agenda: str,
                        max_leads: int, search_depth: int) -> Dict[str, Any]:
        """
        Validate and format user inputs
        
        Args:
            search_strategy: Search strategy for finding leads
            target_clients: Target clients string
            campaign_agenda: Campaign agenda
            max_leads: Maximum leads
            search_depth: Search depth
            
        Returns:
            Validated user input dictionary
        """
        # Validate required fields
        if not search_strategy or not search_strategy.strip():
            raise ValueError("Search strategy is required")
        
        if not target_clients or not target_clients.strip():
            raise ValueError("Target clients are required")
        
        if not campaign_agenda or not campaign_agenda.strip():
            raise ValueError("Campaign agenda is required")
        
        # Validate numeric fields
        if not isinstance(max_leads, int) or max_leads < 1 or max_leads > 1000:
            raise ValueError("Maximum leads must be between 1 and 1000")
        
        if not isinstance(search_depth, int) or search_depth < 1 or search_depth > 5:
            raise ValueError("Search depth must be between 1 and 5")
        
        # Parse target clients
        target_clients_list = [client.strip() for client in target_clients.split(',') if client.strip()]
        if not target_clients_list:
            raise ValueError("At least one target client is required")
        
        return {
            'search_strategy': search_strategy.strip(),
            'target_clients': target_clients_list,
            'campaign_agenda': campaign_agenda.strip(),
            'max_leads': max_leads,
            'search_depth': search_depth
        }
    
    def _format_success_result(self, user_input: Dict[str, Any], result: Dict[str, Any], 
                              final_state: Dict[str, Any]) -> str:
        """
        Format successful workflow result
        
        Args:
            user_input: User input dictionary
            result: Workflow result
            final_state: Final workflow state
            
        Returns:
            Formatted success result string
        """
        output = f"""# ✅ Lead Generation Workflow Completed Successfully!

## Live Progress Summary:
{self.progress_service.get_live_progress()}

## Configuration Used:
- **Search Strategy**: {user_input['search_strategy']}
- **Target Clients**: {', '.join(user_input['target_clients'])}
- **Campaign Agenda**: {user_input['campaign_agenda']}
- **Max Leads**: {user_input['max_leads']}
- **Search Depth**: {user_input['search_depth']}

## Results:
{result['result']}"""
        
        # Display evaluation results if available
        evaluation = self.progress_service.get_evaluation_results()
        if evaluation:
            output += f"\n{self.progress_service.format_evaluation_results(evaluation)}"
        
        return output
    
    def _format_error_result(self, result: Dict[str, Any]) -> str:
        """
        Format error result
        
        Args:
            result: Workflow result with error
            
        Returns:
            Formatted error result string
        """
        return f"# ❌ Workflow Failed\n\n**Error**: {result['error']}\n\n**Progress**: {self.progress_service.get_live_progress()}"
    
    def _format_exception_result(self, error_message: str) -> str:
        """
        Format exception result
        
        Args:
            error_message: Exception message
            
        Returns:
            Formatted exception result string
        """
        return f"# ❌ Error\n\n**Error**: {error_message}\n\n**Progress**: {self.progress_service.get_live_progress()}"
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get current workflow status
        
        Returns:
            Workflow status dictionary
        """
        return self.progress_service.get_workflow_status()
    
    def is_workflow_running(self) -> bool:
        """
        Check if workflow is currently running
        
        Returns:
            True if workflow is running, False otherwise
        """
        state = self.progress_service.get_workflow_status()
        return state['workflow_status'] == 'running'
    
    def get_workflow_progress(self) -> str:
        """
        Get current workflow progress
        
        Returns:
            Formatted progress string
        """
        return self.progress_service.get_live_progress()
    
    def get_analytics_summary(self) -> str:
        """
        Get analytics summary
        
        Returns:
            Formatted analytics summary
        """
        return self.progress_service.get_analytics_summary()
    
    def get_email_service_status(self) -> str:
        """
        Get email service status and configuration
        
        Returns:
            Email service status message
        """
        return self.email_service.get_api_status_message()
    
    def is_email_validation_available(self) -> bool:
        """
        Check if email validation is available
        
        Returns:
            True if email validation is configured, False otherwise
        """
        return self.email_service.is_api_configured() 