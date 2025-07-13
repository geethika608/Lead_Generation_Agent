"""
Modular DeepEval evaluator for lead generation workflow
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List
from prometheus_client import Counter, Histogram
from ..monitoring.prometheus_metrics import record_evaluation_result

# Import modular components
from .metrics_config import MetricsConfig
from .test_case_builder import TestCaseBuilder
from .feedback_generator import FeedbackGenerator
from .agent_expectations import get_agent_expectation, list_all_agents

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepEvalEvaluator:
    """Comprehensive evaluator for lead generation workflow using DeepEval"""
    
    def __init__(self, api_key: Optional[str] = None, custom_thresholds: Optional[dict] = None):
        """
        Initialize the DeepEval evaluator
        
        Args:
            api_key: API key for evaluation service (optional)
            custom_thresholds: Custom thresholds for metrics (optional)
        """
        if not MetricsConfig.is_available():
            raise ImportError("DeepEval is not available. Install with: pip install deepeval")
        
        self.api_key = api_key or os.getenv('DEEPEVAL_API_KEY')
        self.evaluation_threshold = 0.7  # Default pass threshold
        
        # Initialize DeepEval metrics
        self.metrics = MetricsConfig.get_metrics(custom_thresholds)
        self.weights = MetricsConfig.get_weights()
        
    def evaluate_agent_output(self, agent_name: str, task_name: str, output: Any, expected_output_type: str) -> Dict[str, Any]:
        """
        Evaluate a specific agent's output using DeepEval
        
        Args:
            agent_name: Name of the agent
            task_name: Name of the task
            output: Agent's output
            expected_output_type: Expected output type/format
            
        Returns:
            Dictionary with evaluation results
        """
        try:
            # Create test case for DeepEval
            test_case = TestCaseBuilder.create_agent_test_case(agent_name, task_name, output)
            
            # Run evaluation with DeepEval
            evaluation_result = self._run_deepeval_evaluation(test_case)
            
            # Calculate overall score
            score = self._calculate_overall_score(evaluation_result)
            
            # Determine if evaluation passed
            passed = score >= self.evaluation_threshold
            
            # Record metrics
            record_evaluation_result(score, passed)
            
            return {
                'agent': agent_name,
                'task': task_name,
                'score': score,
                'passed': passed,
                'threshold': self.evaluation_threshold,
                'feedback': FeedbackGenerator.generate_agent_feedback(score, agent_name, task_name),
                'detailed_scores': evaluation_result,
                'timestamp': time.time()
            }
            
        except Exception as e:
            # Record error metric
            record_evaluation_result(0.0, False) # Record a failed evaluation
            logger.error(f"Evaluation failed for {agent_name}/{task_name}: {str(e)}")
            return {
                'agent': agent_name,
                'task': task_name,
                'score': 0.0,
                'passed': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def evaluate_workflow(self, workflow_result: Any) -> Dict[str, Any]:
        """
        Evaluate the entire workflow result using DeepEval
        
        Args:
            workflow_result: Complete workflow result from CrewAI
            
        Returns:
            Dictionary with overall workflow evaluation
        """
        try:
            # Extract key components from workflow result
            workflow_summary = self._extract_workflow_summary(workflow_result)
            
            # Create comprehensive test case
            test_case = TestCaseBuilder.create_workflow_test_case(workflow_summary)
            
            # Run evaluation with DeepEval
            evaluation_result = self._run_deepeval_evaluation(test_case)
            
            # Calculate overall score
            score = self._calculate_overall_score(evaluation_result)
            
            # Determine if workflow passed
            passed = score >= self.evaluation_threshold
            
            # Record metrics
            record_evaluation_result(score, passed)
            
            return {
                'score': score,
                'passed': passed,
                'threshold': self.evaluation_threshold,
                'feedback': FeedbackGenerator.generate_workflow_feedback(score, workflow_summary),
                'detailed_scores': evaluation_result,
                'summary': workflow_summary,
                'timestamp': time.time()
            }
            
        except Exception as e:
            # Record error metric
            record_evaluation_result(0.0, False) # Record a failed workflow evaluation
            logger.error(f"Workflow evaluation failed: {str(e)}")
            return {
                'score': 0.0,
                'passed': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def evaluate_all_agents(self, workflow_result: Any) -> List[Dict[str, Any]]:
        """
        Evaluate all agent outputs in the workflow using DeepEval
        
        Args:
            workflow_result: Complete workflow result from CrewAI
            
        Returns:
            List of evaluation results for each agent
        """
        evaluations = []
        
        # Extract agent outputs from workflow result
        if hasattr(workflow_result, 'raw') and isinstance(workflow_result.raw, dict):
            result_data = workflow_result.raw
            
            # Evaluate individual agents based on their outputs
            agent_evaluations = []
            
                    # Removed search_planner_agent evaluation
            
            if 'scraper_agent' in result_data:
                agent_evaluations.append(self._evaluate_scraper(result_data['scraper_agent']))
            
            if 'email_validator_agent' in result_data:
                agent_evaluations.append(self._evaluate_email_validator(result_data['email_validator_agent']))
            
            if 'data_analytics_agent' in result_data:
                agent_evaluations.append(self._evaluate_data_analytics(result_data['data_analytics_agent']))
            
            return agent_evaluations
        
        return evaluations
    
    def _run_deepeval_evaluation(self, test_case) -> Dict[str, float]:
        """Run DeepEval evaluation on test case"""
        try:
            # Run evaluation with all metrics
            results = {}
            for metric in self.metrics:
                try:
                    score = metric.measure(test_case)
                    results[metric.__class__.__name__] = score
                except Exception as e:
                    logger.warning(f"Metric {metric.__class__.__name__} failed: {str(e)}")
                    results[metric.__class__.__name__] = 0.5  # Default neutral score
            
            return results
            
        except Exception as e:
            logger.error(f"DeepEval evaluation failed: {str(e)}")
            # Return default scores
            return {
                'AnswerRelevancy': 0.5,
                'Faithfulness': 0.5,
                'ContextRelevancy': 0.5,
                'ContextRecall': 0.5,
                'AnswerCorrectness': 0.5
            }
    
    def _calculate_overall_score(self, detailed_scores: Dict[str, float]) -> float:
        """Calculate overall score from detailed metric scores"""
        if not detailed_scores:
            return 0.5
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric_name, score in detailed_scores.items():
            weight = self.weights.get(metric_name, 0.1)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _extract_workflow_summary(self, workflow_result: Any) -> Dict[str, Any]:
        """Extract key information from workflow result for evaluation"""
        summary = {
            'tasks_completed': [],
            'leads_generated': 0,
            'emails_validated': 0,
            'data_stored': False,
            'errors': []
        }
        
        try:
            if hasattr(workflow_result, 'raw') and isinstance(workflow_result.raw, dict):
                result_data = workflow_result.raw
                
                # Check for key workflow components
                workflow_components = {
                    'lead_scraping': 'scraper_agent' in result_data,
                    'email_validation': 'email_validator_agent' in result_data,
                    'data_storage': 'data_analytics_agent' in result_data
                }
                
                # Check which tasks completed
                for task in list_all_agents():
                    if task in result_data:
                        summary['tasks_completed'].append(task)
                
                # Extract lead count
                if 'scraper_agent' in result_data:
                    leads_data = result_data['scraper_agent']
                    if isinstance(leads_data, dict) and 'leads' in leads_data:
                        summary['leads_generated'] = len(leads_data['leads'])
                    elif isinstance(leads_data, list):
                        summary['leads_generated'] = len(leads_data)
                
                # Check email validation
                if 'email_validator_agent' in result_data:
                    emails_data = result_data['email_validator_agent']
                    if isinstance(emails_data, list):
                        summary['emails_validated'] = len(emails_data)
                    elif isinstance(emails_data, dict) and 'leads' in emails_data:
                        summary['emails_validated'] = len(emails_data['leads'])
                
                # Check data storage
                if 'data_analytics_agent' in result_data:
                    summary['data_stored'] = True
                    
        except Exception as e:
            summary['errors'].append(f"Error extracting summary: {str(e)}")
        
        return summary 