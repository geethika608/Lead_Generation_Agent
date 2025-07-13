"""
Progress service for tracking workflow progress and analytics
"""

import logging
from typing import Dict, Any, Optional
from ..models.analytics_models import WorkflowAnalytics

# Set up logging
logger = logging.getLogger(__name__)

class ProgressService:
    """Service for tracking and reporting workflow progress"""
    
    def __init__(self):
        self.current_progress = []
        self.analytics = WorkflowAnalytics()
        self.evaluation_results = None
        self.workflow_status = "idle"  # idle, running, completed, failed
        self.workflow_start_time = None
        self.workflow_end_time = None
    
    def update_progress(self, step: str, status: str = "completed", details: str = ""):
        """Update progress with a new step"""
        progress_item = {
            "step": step,
            "status": status,
            "details": details,
            "timestamp": "now"
        }
        self.current_progress.append(progress_item)
        logger.info(f"Progress updated: {step} - {status}")
    
    def update_analytics(self, analytics_data: Dict[str, Any]):
        """Update analytics data"""
        try:
            self.analytics = WorkflowAnalytics(**analytics_data)
            logger.info(f"Analytics updated: {self.analytics}")
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    def update_evaluation_results(self, evaluation_data: Dict[str, Any]):
        """Update evaluation results"""
        self.evaluation_results = evaluation_data
        logger.info(f"Evaluation results updated: {evaluation_data}")
    
    def start_workflow(self):
        """Mark workflow as started"""
        self.workflow_status = "running"
        self.workflow_start_time = "now"
        logger.info("Workflow started")
    
    def complete_workflow(self, success: bool = True):
        """Mark workflow as completed"""
        self.workflow_status = "completed" if success else "failed"
        self.workflow_end_time = "now"
        logger.info(f"Workflow completed with status: {self.workflow_status}")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "workflow_status": self.workflow_status,
            "start_time": self.workflow_start_time,
            "end_time": self.workflow_end_time,
            "progress_count": len(self.current_progress),
            "has_analytics": self.analytics is not None,
            "has_evaluation": self.evaluation_results is not None
        }
    
    def is_workflow_completed(self) -> bool:
        """Check if workflow is completed"""
        return self.workflow_status in ["completed", "failed"]
    
    def get_live_progress(self) -> str:
        """Get current progress as formatted string"""
        if not self.current_progress:
            return "Ready to start workflow..."
        
        progress_lines = ["## 📊 Current Progress"]
        for item in self.current_progress:
            status_icon = "✅" if item["status"] == "completed" else "🔄"
            progress_lines.append(f"{status_icon} **{item['step']}**: {item['details']}")
        
        return "\n".join(progress_lines)
    
    def get_analytics_summary(self) -> str:
        """Get analytics summary"""
        if not self.analytics:
            return "No analytics data available"
        
        summary = f"""## 📈 Analytics Summary

### 🎯 Lead Generation
- **Total Leads Found**: {self.analytics.leads_found}
- **Execution Time**: {self.analytics.execution_time:.2f} seconds
- **Success Rate**: {self.analytics.success_rate:.1%}

"""
        
        if self.analytics.evaluation_score is not None:
            summary += f"- **Evaluation Score**: {self.analytics.evaluation_score:.2f}\n"
        
        return summary
    
    def get_evaluation_results(self) -> Optional[Dict[str, Any]]:
        """Get evaluation results"""
        return self.evaluation_results
    
    def format_evaluation_results(self, evaluation: Optional[Dict[str, Any]]) -> str:
        """Format evaluation results as string"""
        if not evaluation:
            return "No evaluation results available"
        
        formatted = "## 🎯 Evaluation Results\n\n"
        
        if 'score' in evaluation:
            score = evaluation['score']
            formatted += f"**Overall Score**: {score:.2f}\n\n"
            
            if score >= 0.8:
                formatted += "🎉 **Excellent Performance**\n"
            elif score >= 0.6:
                formatted += "✅ **Good Performance**\n"
            elif score >= 0.4:
                formatted += "⚠️ **Needs Improvement**\n"
            else:
                formatted += "❌ **Poor Performance**\n"
        
        if 'details' in evaluation:
            formatted += f"\n**Details**: {evaluation['details']}\n"
        
        return formatted
    
    def reset(self):
        """Reset progress and analytics"""
        self.current_progress = []
        self.analytics = WorkflowAnalytics()
        self.evaluation_results = None
        self.workflow_status = "idle"
        self.workflow_start_time = None
        self.workflow_end_time = None
        logger.info("Progress service reset") 