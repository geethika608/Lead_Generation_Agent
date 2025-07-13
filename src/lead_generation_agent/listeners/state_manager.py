import threading
import time
import json
from typing import Dict, Any, Optional
from ..models.analytics_models import WorkflowAnalytics, AgentExecutionRecord

# Task mapping for progress tracking
TASK_NAMES = {
    'scrape_leads': 'Lead Scraping',
    'find_lead_emails': 'Email Finding',
    'validate_lead_emails': 'Email Validation',
    'save_data': 'Data Storage'
}

class WorkflowStateManager:
    """Manages the state of the workflow execution with thread-safe operations"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._state = self._initialize_state()
        self._analytics = WorkflowAnalytics()  # Pydantic analytics model
        
        self._task_order = list(TASK_NAMES.keys())

    def _initialize_state(self) -> Dict[str, Any]:
        """Initialize the workflow state"""
        return {
            'workflow_status': 'idle',  # idle, running, completed, failed
            'current_agent': None,
            'current_task': None,
            'current_tool': None,
            'progress': {
                'completed_tasks': [],
                'total_tasks': 4,  # Based on our workflow
                'current_step': 0
            },
            'analytics': {
                'leads_found': 0
            },
            'timing': {
                'start_time': None,
                'current_task_start': None,
                'estimated_completion': None
            },
            'errors': [],
            'last_update': time.time()
        }

    def reset_state(self):
        """Reset the state for a new workflow execution"""
        with self._lock:
            self._state = self._initialize_state()

    def update_workflow_status(self, status: str):
        """Update the workflow status"""
        with self._lock:
            self._state['workflow_status'] = status
            self._state['last_update'] = time.time()

    def update_current_agent(self, agent_role: Optional[str]):
        """Update the current agent"""
        with self._lock:
            self._state['current_agent'] = agent_role
            self._state['last_update'] = time.time()

    def update_current_task(self, task_name: Optional[str]):
        """Update the current task and progress"""
        with self._lock:
            if task_name:
                self._state['current_task'] = TASK_NAMES.get(task_name, task_name)
                self._state['timing']['current_task_start'] = time.time()
                
                # Update progress
                if task_name in self._task_order:
                    self._state['progress']['current_step'] = self._task_order.index(task_name) + 1
            else:
                self._state['current_task'] = None
            
            self._state['last_update'] = time.time()

    def update_current_tool(self, tool_name: Optional[str]):
        """Update the current tool"""
        with self._lock:
            self._state['current_tool'] = tool_name
            self._state['last_update'] = time.time()

    def add_completed_task(self, task_name: str):
        """Add a completed task to the progress"""
        with self._lock:
            completed_task = TASK_NAMES.get(task_name, task_name)
            if completed_task not in self._state['progress']['completed_tasks']:
                self._state['progress']['completed_tasks'].append(completed_task)
            self._state['last_update'] = time.time()

    def add_error(self, error: str):
        """Add an error to the error list"""
        with self._lock:
            self._state['errors'].append(error)
            self._state['last_update'] = time.time()

    def update_analytics(self, analytics_updates: Dict[str, Any]):
        """Update analytics with new data"""
        with self._lock:
            for key, value in analytics_updates.items():
                if key in self._state['analytics']:
                    self._state['analytics'][key] = value
            self._state['last_update'] = time.time()

    def update_evaluation_results(self, evaluation_results: Dict[str, Any]):
        """Update evaluation results from DeepEval"""
        with self._lock:
            if 'evaluation' not in self._state:
                self._state['evaluation'] = {}
            
            self._state['evaluation'].update(evaluation_results)
            self._state['last_update'] = time.time()

    def process_agent_output(self, agent_name: str, task_name: str, output: Any, success: bool = True, error_message: str = None, execution_time: float = None):
        """Process agent output using Pydantic models and update analytics"""
        with self._lock:
            try:
                # Create structured agent output
                agent_output = AgentExecutionRecord(
                    agent_name=agent_name,
                    task_name=task_name,
                    output_data=output,
                    success=success,
                    error_message=error_message,
                    execution_time=execution_time
                )
                
                # Extract analytics from the output
                new_analytics = agent_output.extract_analytics()
                
                # Update the Pydantic analytics model
                self._analytics.leads_found = max(self._analytics.leads_found, new_analytics.leads_found)
                
                # Sync Pydantic model to state dict
                self._sync_analytics_to_state()
                
                self._state['last_update'] = time.time()
                
            except Exception as e:
                print(f"Error processing agent output: {e}")
                # Fallback to old method if Pydantic processing fails
                if isinstance(output, dict):
                    self.update_analytics(output)

    def _sync_analytics_to_state(self):
        """Sync Pydantic analytics model to state dictionary"""
        self._state['analytics'] = {
            'leads_found': self._analytics.leads_found
        }

    def set_start_time(self):
        """Set the workflow start time"""
        with self._lock:
            self._state['timing']['start_time'] = time.time()
            self._state['last_update'] = time.time()

    def get_state(self) -> Dict[str, Any]:
        """Get current state for UI updates"""
        with self._lock:
            # Calculate progress percentage
            progress_percentage = (len(self._state['progress']['completed_tasks']) / 
                                 self._state['progress']['total_tasks']) * 100
            
            # Calculate estimated completion time
            estimated_completion = None
            if (self._state['timing']['start_time'] and 
                self._state['timing']['current_task_start'] and
                self._state['progress']['current_step'] > 0):
                
                elapsed = time.time() - self._state['timing']['start_time']
                avg_time_per_task = elapsed / self._state['progress']['current_step']
                remaining_tasks = self._state['progress']['total_tasks'] - self._state['progress']['current_step']
                estimated_completion = time.time() + (avg_time_per_task * remaining_tasks)
            
            return {
                'workflow_status': self._state['workflow_status'],
                'current_agent': self._state['current_agent'],
                'current_task': self._state['current_task'],
                'current_tool': self._state['current_tool'],
                'progress': {
                    'percentage': round(progress_percentage, 1),
                    'completed_tasks': self._state['progress']['completed_tasks'],
                    'total_tasks': self._state['progress']['total_tasks'],
                    'current_step': self._state['progress']['current_step']
                },
                'analytics': self._state['analytics'],
                'timing': {
                    'start_time': self._state['timing']['start_time'],
                    'current_task_start': self._state['timing']['current_task_start'],
                    'estimated_completion': estimated_completion
                },
                'errors': self._state['errors'],
                'last_update': self._state['last_update']
            }

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary for reporting"""
        with self._lock:
            return {
                'leads_found': self._analytics.leads_found,
                'execution_time': self._analytics.execution_time,
                'success_rate': self._analytics.success_rate,
                'evaluation_score': self._analytics.evaluation_score
            }

# Global state manager instance
workflow_state_manager = WorkflowStateManager() 