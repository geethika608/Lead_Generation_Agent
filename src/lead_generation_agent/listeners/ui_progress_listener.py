import logging
from typing import Dict, Any, List
from ..models.analytics_models import WorkflowAnalytics

logger = logging.getLogger(__name__)

class UIProgressListener:
    """Listener for tracking UI progress and analytics"""
    
    def __init__(self):
        self.state = {
            'workflow_status': 'idle',
            'current_agent': None,
            'current_task': None,
            'current_tool': None,
            'progress': {
                'percentage': 0,
                'completed_tasks': [],
                'total_tasks': 0
            },
            'analytics': {
                'leads_found': 0
            },
            'evaluation': {}
        }
        self.task_list = [
            'scrape_leads',
            'find_lead_emails', 
            'validate_lead_emails',
            'save_data'
        ]
    
    def on_workflow_start(self):
        """Called when workflow starts"""
        self.state['workflow_status'] = 'running'
        self.state['progress']['total_tasks'] = len(self.task_list)
        self.state['progress']['completed_tasks'] = []
        self.state['progress']['percentage'] = 0
        logger.info("Workflow started")
    
    def on_workflow_complete(self, success: bool = True):
        """Called when workflow completes"""
        self.state['workflow_status'] = 'completed' if success else 'failed'
        self.state['current_agent'] = None
        self.state['current_task'] = None
        self.state['current_tool'] = None
        self.state['progress']['percentage'] = 100
        logger.info(f"Workflow completed with success={success}")
    
    def on_agent_start(self, agent_name: str):
        """Called when an agent starts"""
        self.state['current_agent'] = agent_name
        logger.info(f"Agent started: {agent_name}")
    
    def on_agent_complete(self, agent_name: str, success: bool = True):
        """Called when an agent completes"""
        if self.state['current_agent'] == agent_name:
            self.state['current_agent'] = None
        logger.info(f"Agent completed: {agent_name} (success={success})")
    
    def on_task_start(self, task_name: str):
        """Called when a task starts"""
        self.state['current_task'] = task_name
        logger.info(f"Task started: {task_name}")
    
    def on_task_complete(self, task_name: str, success: bool = True):
        """Called when a task completes"""
        if self.state['current_task'] == task_name:
            self.state['current_task'] = None
        
        if success and task_name not in self.state['progress']['completed_tasks']:
            self.state['progress']['completed_tasks'].append(task_name)
        
        # Update percentage
        completed = len(self.state['progress']['completed_tasks'])
        total = self.state['progress']['total_tasks']
        if total > 0:
            self.state['progress']['percentage'] = int((completed / total) * 100)
        
        logger.info(f"Task completed: {task_name} (success={success})")
    
    def on_tool_start(self, tool_name: str):
        """Called when a tool starts"""
        self.state['current_tool'] = tool_name
        logger.info(f"Tool started: {tool_name}")
    
    def on_tool_complete(self, tool_name: str, success: bool = True):
        """Called when a tool completes"""
        if self.state['current_tool'] == tool_name:
            self.state['current_tool'] = None
        logger.info(f"Tool completed: {tool_name} (success={success})")
    
    def update_analytics(self, analytics_data: Dict[str, Any]):
        """Update analytics data"""
        if 'leads_found' in analytics_data:
            self.state['analytics']['leads_found'] = analytics_data['leads_found']
        logger.info(f"Analytics updated: {analytics_data}")
    
    def update_evaluation(self, evaluation_data: Dict[str, Any]):
        """Update evaluation data"""
        self.state['evaluation'] = evaluation_data
        logger.info(f"Evaluation updated: {evaluation_data}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        return self.state.copy()
    
    def reset(self):
        """Reset the listener state"""
        self.state = {
            'workflow_status': 'idle',
            'current_agent': None,
            'current_task': None,
            'current_tool': None,
            'progress': {
                'percentage': 0,
                'completed_tasks': [],
                'total_tasks': 0
            },
            'analytics': {
                'leads_found': 0
            },
            'evaluation': {}
        }
        logger.info("Progress listener reset")

# Global instance
ui_progress_listener = UIProgressListener() 