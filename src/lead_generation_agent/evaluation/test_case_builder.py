"""
Test case builder for DeepEval evaluation
"""

import json
from typing import Dict, Any
from .agent_expectations import get_sample_output, get_agent_description

# DeepEval imports
try:
    from deepeval.test_case import LLMTestCase
    DEEPEVAL_AVAILABLE = True
except ImportError:
    DEEPEVAL_AVAILABLE = False

class TestCaseBuilder:
    """Builder for DeepEval test cases"""
    
    @staticmethod
    def create_agent_test_case(agent_name: str, task_name: str, output: Any) -> LLMTestCase:
        """Create DeepEval test case for agent output evaluation"""
        if not DEEPEVAL_AVAILABLE:
            raise ImportError("DeepEval is not available. Install with: pip install deepeval")
        
        # Convert output to string for evaluation
        output_str = json.dumps(output, indent=2) if isinstance(output, (dict, list)) else str(output)
        
        # Get sample output for comparison
        sample_output = get_sample_output(agent_name)
        sample_output_str = json.dumps(sample_output, indent=2) if sample_output else "No sample available"
        
        # Get agent description
        description = get_agent_description(agent_name)
        
        # Create context and expected output
        context = f"""
        Task: {task_name}
        Agent: {agent_name}
        Expected Output Type: {description}
        
        Sample Expected Output:
        {sample_output_str}
        """
        
        expected_output = f"""
        Complete, well-structured output matching {description} format.
        The output should contain all required fields and follow the structure shown in the sample.
        Quality indicators:
        - All required fields are present
        - Data is properly formatted
        - Content is relevant and professional
        - Structure matches the expected model
        """
        
        return LLMTestCase(
            input=context,
            actual_output=output_str,
            expected_output=expected_output,
            context=context
        )
    
    @staticmethod
    def create_workflow_test_case(workflow_summary: Dict[str, Any]) -> LLMTestCase:
        """Create DeepEval test case for workflow evaluation"""
        if not DEEPEVAL_AVAILABLE:
            raise ImportError("DeepEval is not available. Install with: pip install deepeval")
        
        # Create comprehensive workflow description
        workflow_description = TestCaseBuilder._create_workflow_description(workflow_summary)
        
        # Create expected workflow output
        expected_output = "Complete lead generation workflow with high-quality leads, comprehensive campaign strategy, professional email templates, and proper data organization"
        
        return LLMTestCase(
            input=workflow_description,
            actual_output=json.dumps(workflow_summary, indent=2),
            expected_output=expected_output,
            context=workflow_description
        )
    
    @staticmethod
    def _create_workflow_description(workflow_summary: Dict[str, Any]) -> str:
        """Create comprehensive workflow description for evaluation"""
        tasks_completed = workflow_summary.get('tasks_completed', [])
        leads_generated = workflow_summary.get('leads_generated', 0)
        emails_generated = workflow_summary.get('emails_generated', 0)
        data_stored = workflow_summary.get('data_stored', False)
        
        return f"""
        Lead Generation Workflow Summary:
        
        Tasks Completed: {len(tasks_completed)}/6
        # Removed Lead Generation Planning (search_planner_agent)
        - Lead Scraping: {'scraper_agent' in tasks_completed}
        - Email Validation: {'email_validator_agent' in tasks_completed}
        - Email Templates: {'email_creator_agent' in tasks_completed}
        - Spam Checking: {'spam_checker_agent' in tasks_completed}
        - Data Storage: {'data_analytics_agent' in tasks_completed}
        
        Results:
        - Leads Generated: {leads_generated}
        - Emails Generated: {emails_generated}
        - Data Stored: {data_stored}
        
        Expected: Complete workflow execution with high-quality outputs
        """ 