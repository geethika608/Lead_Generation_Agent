from typing import Any, Dict
from .state_manager import WorkflowStateManager
from .analytics_parser import AnalyticsParser
from ..monitoring.prometheus_metrics import record_agent_execution, record_task_execution
import time
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

class EventHandlers:
    """Handles different types of CrewAI events"""
    
    def __init__(self, state_manager: WorkflowStateManager, analytics_parser: AnalyticsParser):
        self.state_manager = state_manager
        self.analytics_parser = analytics_parser
        # For timing agent/task execution
        self._agent_start_times = {}
        self._task_start_times = {}
        # Initialize DeepEval evaluator if available
        self._evaluator = None
        self._initialize_evaluator()

    def _initialize_evaluator(self):
        """Initialize DeepEval evaluator if API key is available"""
        try:
            deepeval_api_key = os.getenv('DEEPEVAL_API_KEY')
            if deepeval_api_key:
                from ..evaluation.deepeval_evaluator import DeepEvalEvaluator
                self._evaluator = DeepEvalEvaluator(deepeval_api_key)
                logger.info("DeepEval evaluator initialized successfully")
            else:
                logger.info("DeepEval API key not found, evaluation will be skipped")
        except ImportError as e:
            logger.warning(f"DeepEval not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize DeepEval evaluator: {e}")

    def handle_crew_start(self, event: Dict[str, Any]):
        """Handle crew start event"""
        self.state_manager.set_start_time()
        self.state_manager.update_workflow_status('running')
        self.state_manager.update_current_agent(None)
        self.state_manager.update_current_task(None)
        self.state_manager.update_current_tool(None)

    def handle_crew_end(self, event: Dict[str, Any]):
        """Handle crew end event"""
        self.state_manager.update_workflow_status('completed')
        self.state_manager.update_current_agent(None)
        self.state_manager.update_current_task(None)
        self.state_manager.update_current_tool(None)
        
        # Extract final analytics from result
        if 'result' in event:
            analytics = self.analytics_parser.extract_analytics_from_result(event['result'])
            self.state_manager.update_analytics(analytics)
            
            # Run DeepEval evaluation if available
            if self._evaluator:
                try:
                    self._run_evaluation(event['result'])
                except Exception as e:
                    logger.error(f"Evaluation failed: {e}")

    def _run_evaluation(self, workflow_result):
        """Run DeepEval evaluation on workflow result"""
        workflow_evaluation = None
        agent_evaluations = []
        
        try:
            # Evaluate individual agents
            agent_evaluations = self._evaluator.evaluate_all_agents(workflow_result)
            
            # Evaluate overall workflow
            workflow_evaluation = self._evaluator.evaluate_workflow(workflow_result)
            
            # Store evaluation results in state
            evaluation_results = {
                'workflow_evaluation': workflow_evaluation,
                'agent_evaluations': agent_evaluations,
                'evaluation_enabled': True
            }
            
            self.state_manager.update_evaluation_results(evaluation_results)
            
            # Log success with safe access to score
            if workflow_evaluation and 'score' in workflow_evaluation:
                logger.info(f"Evaluation completed - Workflow score: {workflow_evaluation['score']:.2f}")
            else:
                logger.info("Evaluation completed - No score available")
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            # Store error in evaluation results
            error_results = {
                'workflow_evaluation': {'error': str(e)},
                'agent_evaluations': agent_evaluations,
                'evaluation_enabled': False
            }
            self.state_manager.update_evaluation_results(error_results)

    def handle_agent_start(self, event: Dict[str, Any]):
        """Handle agent start event"""
        agent_role = event.get('agent', {}).get('role', 'Unknown Agent')
        self.state_manager.update_current_agent(agent_role)
        self.state_manager.update_current_task(None)
        self.state_manager.update_current_tool(None)
        # Record agent start time
        self._agent_start_times[agent_role] = time.time()

    def handle_agent_end(self, event: Dict[str, Any]):
        """Handle agent end event"""
        agent_role = event.get('agent', {}).get('role', 'Unknown Agent')
        # Record agent execution duration and count
        start_time = self._agent_start_times.pop(agent_role, None)
        duration = time.time() - start_time if start_time else 0.0
        record_agent_execution(agent=agent_role, duration=duration, error=False)
        # Keep current agent info until next agent starts
        pass

    def handle_task_start(self, event: Dict[str, Any]):
        """Handle task start event"""
        task_name = event.get('task', {}).get('description', 'Unknown Task')
        # Extract task name from description
        task_key = self._extract_task_key(task_name)
        self.state_manager.update_current_task(task_key)
        # Record task start time
        self._task_start_times[task_key] = time.time()

    def handle_task_end(self, event: Dict[str, Any]):
        """Handle task end event"""
        task_name = event.get('task', {}).get('description', 'Unknown Task')
        task_key = self._extract_task_key(task_name)
        
        # Mark task as completed
        self.state_manager.add_completed_task(task_key)
        
        # Record task execution duration and count
        start_time = self._task_start_times.pop(task_key, None)
        duration = time.time() - start_time if start_time else 0.0
        record_task_execution(task=task_key, duration=duration, error=False)
        
        # Process agent output using Pydantic models
        if 'output' in event and event['output']:
            agent_name = self._extract_agent_name_from_task(task_key)
            execution_time = event.get('execution_time')
            
            # Process the output with Pydantic models
            self.state_manager.process_agent_output(
                agent_name=agent_name,
                task_name=task_key,
                output=event['output'],
                success=True,
                execution_time=execution_time
            )
            
            # Also run legacy analytics parser as backup
            task_analytics = self.analytics_parser.parse_task_output(task_key, str(event['output']))
            self.state_manager.update_analytics(task_analytics)

    # Tool event handlers removed to simplify implementation
    # def handle_tool_start(self, event: Dict[str, Any]):
    #     """Handle tool start event"""
    #     tool_name = event.get('tool', {}).get('name', 'Unknown Tool')
    #     self.state_manager.update_current_tool(tool_name)
    #     self.state_manager.increment_tool_usage(tool_name)

    # def handle_tool_end(self, event: Dict[str, Any]):
    #     """Handle tool end event"""
    #     # Keep current tool info until next tool starts
    #     pass

    # Temporarily disabled LLM event handlers to avoid attribute errors
    # def handle_llm_start(self, event: Dict[str, Any]):
    #     """Handle LLM start event"""
    #     self.state_manager.increment_llm_calls()

    # def handle_llm_end(self, event: Dict[str, Any]):
    #     """Handle LLM end event"""
    #     # Analytics are already incremented in start
    #     pass

    def handle_error(self, event: Dict[str, Any]):
        """Handle error event"""
        error_message = event.get('error', 'Unknown error occurred')
        self.state_manager.add_error(str(error_message))
        self.state_manager.update_workflow_status('failed')
        # If error is from agent or task, record error metric
        agent = event.get('agent', {}).get('role')
        task = event.get('task', {}).get('description')
        if agent:
            record_agent_execution(agent=agent, duration=0.0, error=True)
        if task:
            task_key = self._extract_task_key(task)
            record_task_execution(task=task_key, duration=0.0, error=True)

    def _extract_task_key(self, task_description: str) -> str:
        """Extract task key from task description"""
        task_description_lower = task_description.lower()
        
        if 'user input' in task_description_lower or 'collect' in task_description_lower:
            return 'collect_user_input'
        elif 'scrape' in task_description_lower or 'lead' in task_description_lower:
            return 'scrape_leads'
        elif 'validate' in task_description_lower or 'email validation' in task_description_lower:
            return 'validate_lead_emails'
        elif 'save' in task_description_lower or 'data' in task_description_lower:
            return 'save_data'
        else:
            return 'unknown_task'

    def _extract_agent_name_from_task(self, task_key: str) -> str:
        """Extract agent name from task key"""
        task_to_agent_mapping = {
            'collect_user_input': 'user_input_agent',
            'scrape_leads': 'scraper_agent',
            'validate_lead_emails': 'email_validator_agent',
            'save_data': 'data_analytics_agent'
        }
        return task_to_agent_mapping.get(task_key, 'unknown_agent') 