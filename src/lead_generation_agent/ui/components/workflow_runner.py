"""
Workflow execution UI component for the Gradio interface
"""

import gradio as gr
from ...services.workflow_service import WorkflowService

class WorkflowRunner:
    """Workflow execution UI component"""
    
    def __init__(self):
        """Initialize workflow runner"""
        self.workflow_service = WorkflowService()
    
    def create_workflow_section(self) -> tuple:
        """Create the workflow execution section"""
        with gr.Column(scale=1):
            # Results Section
            gr.HTML('<div class="output-section">')
            
            gr.HTML("<h3>📋 Results</h3>")
            
            output = gr.Markdown(
                value="",
                label="Workflow Results"
            )
            
            gr.HTML('</div>')
            
            return output
    
    def run_lead_generation(self, search_strategy: str, target_clients: str, campaign_agenda: str,
                           max_leads: int, search_depth: int, session_id: str = None, progress_fn=None) -> str:
        """Run the lead generation workflow using the service"""
        return self.workflow_service.run_lead_generation(
            search_strategy, target_clients, campaign_agenda, max_leads, search_depth, session_id, progress_fn
        )
    
    def get_workflow_status(self) -> dict:
        """Get workflow status from the service"""
        return self.workflow_service.get_workflow_status()
    
    def is_workflow_running(self) -> bool:
        """Check if workflow is running using the service"""
        return self.workflow_service.is_workflow_running()
    
    def get_workflow_progress(self) -> str:
        """Get workflow progress from the service"""
        return self.workflow_service.get_workflow_progress()
    
    def get_analytics_summary(self) -> str:
        """Get analytics summary from the service"""
        return self.workflow_service.get_analytics_summary() 