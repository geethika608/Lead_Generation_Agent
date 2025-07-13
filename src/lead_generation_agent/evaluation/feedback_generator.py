"""
Feedback generator for DeepEval evaluation results
"""

from typing import Dict, Any

class FeedbackGenerator:
    """Generator for evaluation feedback"""
    
    @staticmethod
    def generate_agent_feedback(score: float, agent_name: str, task_name: str) -> str:
        """Generate feedback based on evaluation score for agent output"""
        if score >= 0.9:
            return f"Excellent performance by {agent_name} on {task_name}. Output exceeds expectations."
        elif score >= 0.7:
            return f"Good performance by {agent_name} on {task_name}. Output meets requirements."
        elif score >= 0.5:
            return f"Acceptable performance by {agent_name} on {task_name}. Some improvements needed."
        else:
            return f"Poor performance by {agent_name} on {task_name}. Significant improvements required."
    
    @staticmethod
    def generate_workflow_feedback(score: float, workflow_summary: Dict[str, Any]) -> str:
        """Generate feedback for entire workflow"""
        if score >= 0.9:
            return "Excellent workflow execution. All objectives achieved with high quality."
        elif score >= 0.7:
            return "Good workflow execution. Most objectives achieved successfully."
        elif score >= 0.5:
            return "Acceptable workflow execution. Some objectives achieved with issues."
        else:
            return "Poor workflow execution. Many objectives not achieved or with significant issues."
    
    @staticmethod
    def generate_detailed_feedback(score: float, detailed_scores: Dict[str, float], agent_name: str = None) -> str:
        """Generate detailed feedback based on individual metric scores"""
        feedback_parts = []
        
        # Overall score feedback
        if score >= 0.9:
            feedback_parts.append("Overall: Excellent performance across all metrics.")
        elif score >= 0.7:
            feedback_parts.append("Overall: Good performance with room for improvement.")
        elif score >= 0.5:
            feedback_parts.append("Overall: Acceptable performance with several areas needing attention.")
        else:
            feedback_parts.append("Overall: Poor performance requiring significant improvements.")
        
        # Individual metric feedback
        for metric_name, metric_score in detailed_scores.items():
            if metric_score >= 0.9:
                feedback_parts.append(f"{metric_name}: Excellent")
            elif metric_score >= 0.7:
                feedback_parts.append(f"{metric_name}: Good")
            elif metric_score >= 0.5:
                feedback_parts.append(f"{metric_name}: Acceptable")
            else:
                feedback_parts.append(f"{metric_name}: Needs improvement")
        
        return " | ".join(feedback_parts)
    
    @staticmethod
    def generate_improvement_suggestions(score: float, detailed_scores: Dict[str, float]) -> list:
        """Generate specific improvement suggestions based on scores"""
        suggestions = []
        
        if score < 0.7:
            suggestions.append("Overall quality needs improvement")
        
        # Specific metric suggestions
        if detailed_scores.get('AnswerRelevancy', 1.0) < 0.7:
            suggestions.append("Improve answer relevance to the task")
        
        if detailed_scores.get('Faithfulness', 1.0) < 0.7:
            suggestions.append("Ensure output faithfully follows the expected format")
        
        if detailed_scores.get('ContextRelevancy', 1.0) < 0.7:
            suggestions.append("Make output more relevant to the given context")
        
        if detailed_scores.get('ContextRecall', 1.0) < 0.7:
            suggestions.append("Include more relevant information from the context")
        
        if detailed_scores.get('AnswerCorrectness', 1.0) < 0.7:
            suggestions.append("Verify the accuracy and correctness of the output")
        
        return suggestions 