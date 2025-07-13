"""
Progress tracking UI component for the Gradio interface
"""

import gradio as gr
from ...services.progress_service import ProgressService

class ProgressTracker:
    """Progress tracking UI component"""
    
    def __init__(self):
        """Initialize progress tracker"""
        self.progress_service = ProgressService()
    
    def create_progress_section(self) -> tuple:
        """Create the progress tracking section"""
        with gr.Column(scale=1):
            # Progress Section
            gr.HTML('<div class="progress-section">')
            gr.HTML("<h3>📊 Live Progress</h3>")
            
            progress_display = gr.Markdown(
                value="",
                label="Current Status",
                every=2.0  # Update every 2 seconds
            )
            
            gr.HTML('</div>')
            
            return progress_display
    
    def get_live_progress(self) -> str:
        """Get current progress from the service"""
        return self.progress_service.get_live_progress()
    
    def get_analytics_summary(self) -> str:
        """Get analytics summary from the service"""
        return self.progress_service.get_analytics_summary()
    
    def get_evaluation_results(self) -> str:
        """Get evaluation results from the service"""
        evaluation = self.progress_service.get_evaluation_results()
        return self.progress_service.format_evaluation_results(evaluation) 