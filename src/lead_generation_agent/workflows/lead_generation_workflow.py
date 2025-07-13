import os
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import mlflow
from .crew import LeadGenerationCrew
from ..evaluation.deepeval_evaluator import DeepEvalEvaluator
from ..monitoring.prometheus_metrics import (
    record_workflow_start, record_workflow_completion, record_evaluation_result,
    record_lead_analytics
)
from ..listeners.ui_progress_listener import ui_progress_listener
from ..models.lead_models import UserInput
from ..models.analytics_models import WorkflowAnalytics
from ..services.mlflow_service import mlflow_service
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_config_with_user_input(config: Dict[str, Any], user_input: Dict[str, Any]) -> Dict[str, Any]:
    """Update configuration with user input values"""
    if user_input:
        config.update({
            'search_strategy': user_input.get('search_strategy'),
            'target_clients': user_input.get('target_clients'),
            'campaign_agenda': user_input.get('campaign_agenda'),
            'max_leads_per_search': user_input.get('max_leads'),
            'search_depth': user_input.get('search_depth')
        })
    return config

def extract_workflow_analytics(result: Any) -> dict:
    """Extract simple analytics and progress from the crew workflow result for UI preview."""
    analytics = {
        'progress': [],
        'leads_found': 0,
        'evaluation_score': None,
        'summary': ''
    }
    # Example: result is a dict with task outputs, or a list of step results
    if isinstance(result, dict):
        # Progress: which tasks completed
        completed = []
        for key in ['scrape_leads', 'find_lead_emails', 'validate_lead_emails', 'save_data']:
            if key in result:
                completed.append(key)
        analytics['progress'] = completed
        # Leads found
        leads_data = result.get('scrape_leads', {}).get('output') or result.get('leads')
        if isinstance(leads_data, dict) and 'leads' in leads_data:
            # Handle LeadList structure
            analytics['leads_found'] = len(leads_data['leads'])
        elif isinstance(leads_data, list):
            # Handle legacy list structure
            analytics['leads_found'] = len(leads_data)

        # Evaluation score
        eval_score = result.get('evaluation', {}).get('score') or result.get('evaluation_score')
        if eval_score is not None:
            analytics['evaluation_score'] = eval_score
        # Summary
        summary = result.get('save_data', {}).get('output') or result.get('summary')
        if summary:
            analytics['summary'] = summary
    return analytics

def run_lead_generation_workflow(user_input: Optional[Dict] = None, user_auth: Optional[Dict] = None, config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Run the lead generation workflow with user inputs and authentication
    
    Args:
        user_input: User input dictionary with domain, target_clients, etc.
        user_auth: User authentication data
        config: Configuration dictionary
        
    Returns:
        Dictionary with workflow results and analytics
    """
    start_time = time.time()
    
    # Start MLflow run
    run_name = f"lead_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        mlflow_service.start_run(run_name=run_name)
        print(f"✅ MLflow run started: {run_name}")
        logger.info(f"MLflow run started: {run_name}")
    except Exception as e:
        print(f"❌ Failed to start MLflow run: {e}")
        logger.error(f"Failed to start MLflow run: {e}")
    
    try:
        # Record workflow start (Prometheus)
        record_workflow_start()
        logger.info("Lead Generation Workflow started")
        
        # Update configuration with user input
        if config is None:
            config = {}
        config = update_config_with_user_input(config, user_input)
        
        # Initialize the crew (no user_input in constructor)
        crew = LeadGenerationCrew()
        
        # Prepare input data for kickoff
        input_data = {
            "search_strategy": user_input.get("search_strategy") if user_input else None,
            "target_clients": user_input.get("target_clients") if user_input else None,
            "campaign_agenda": user_input.get("campaign_agenda") if user_input else None,
            "max_leads": user_input.get("max_leads") if user_input else None,
            "search_depth": user_input.get("search_depth") if user_input else None,
            "current_date": str(datetime.now())
        }
        
        # Add user authentication data to input_data if available
        if user_auth:
            input_data.update({
                "user_id": user_auth.get("user_id") or "default",
                "username": user_auth.get("username") or "default_user",
                "email": user_auth.get("email") or "default@example.com",
                "google_authenticated": user_auth.get("google_authenticated", False),
                "google_email": user_auth.get("google_email") or user_auth.get("email") or "default@example.com"
            })
            print(f"🔐 Added user authentication data to workflow: user_id={input_data['user_id']}, google_authenticated={input_data['google_authenticated']}")
            
            # Warn if Google is not authenticated
            if not input_data['google_authenticated']:
                print("⚠️ WARNING: User is not authenticated with Google. Data saving may fail.")
        else:
            # Provide default values when no user auth is available
            input_data.update({
                "user_id": "default",
                "username": "default_user", 
                "email": "default@example.com",
                "google_authenticated": False,
                "google_email": "default@example.com"
            })
            print("⚠️ No user authentication data provided - using default values")
            print("⚠️ WARNING: No Google authentication. Data saving will likely fail.")
        
        print(f"🚀 Starting crew execution with input data: {input_data}")
        logger.info(f"Input data for crew: {input_data}")
        
        # Debug: Check if user_id is in input_data
        if 'user_id' in input_data:
            print(f"✅ User ID found in input data: {input_data['user_id']}")
            logger.info(f"User ID found in input data: {input_data['user_id']}")
        else:
            print("⚠️ User ID not found in input data")
            logger.warning("User ID not found in input data")
        
        # Execute the crew with input data
        logger.info("Executing CrewAI crew...")
        result = crew.crew().kickoff(input_data)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Record workflow completion (Prometheus)
        record_workflow_completion(duration=execution_time, success=True)
        logger.info("Lead Generation Workflow completed successfully")
        
        # Get final analytics from listener
        final_state = ui_progress_listener.get_state()
        
        # Optional: Run evaluation if DeepEval is configured
        agent_evaluations = []
        workflow_evaluation = None
        
        if config.get('deepeval_api_key'):
            try:
                evaluator = DeepEvalEvaluator(config['deepeval_api_key'])
                
                # Evaluate individual agents
                agent_evaluations = evaluator.evaluate_all_agents(result)
                
                # Evaluate overall workflow
                workflow_evaluation = evaluator.evaluate_workflow(result)
                
                # Log success with safe access to score
                if workflow_evaluation and 'score' in workflow_evaluation:
                    logger.info(f"Evaluation completed - Workflow score: {workflow_evaluation['score']:.2f}")
                else:
                    logger.info("Evaluation completed - No score available")
                
            except Exception as e:
                logger.error(f"Evaluation failed: {str(e)}")
        else:
            logger.info("DeepEval evaluation skipped - no API key configured")
        
        # Record lead analytics (Prometheus)
        analytics_preview = extract_workflow_analytics(result)
        leads_found = analytics_preview.get('leads_found', 0)
        record_lead_analytics(found=leads_found)
        
        result_dict = {
            'status': 'success',
            'result': result.raw if hasattr(result, 'raw') else str(result),
            'execution_time': execution_time,
            'analytics': final_state['analytics'],
            'progress': final_state['progress'],
            'evaluation': workflow_evaluation,
            'agent_evaluations': agent_evaluations,
            'analytics_preview': analytics_preview,
            'config_used': {
                'search_strategy': config.get('search_strategy'),
                'target_clients': config.get('target_clients'),
                'campaign_agenda': config.get('campaign_agenda'),
                'max_leads': config.get('max_leads_per_search'),
                'search_depth': config.get('search_depth'),
                'evaluation_enabled': bool(config.get('deepeval_api_key')),
                'monitoring_enabled': config.get('analytics', {}).get('enable_prometheus', True)
            }
        }
        
        return result_dict
        
    except Exception as e:
        # Record error (Prometheus)
        record_workflow_completion(duration=0, success=False)
        logger.error(f"Workflow failed: {str(e)}")
        
        error_result = {
            'status': 'error',
            'error': str(e),
            'config_used': {
                'search_strategy': config.get('search_strategy') if 'config' in locals() else None,
                'target_clients': config.get('target_clients') if 'config' in locals() else None,
                'campaign_agenda': config.get('campaign_agenda') if 'config' in locals() else None
            }
        }
        
        return error_result
        
    finally:
        # End MLflow run
        try:
            mlflow_service.end_run()
            print(f"✅ MLflow run ended successfully for workflow: {run_name}")
            logger.info("MLflow run ended successfully")
        except Exception as e:
            print(f"❌ Failed to end MLflow run: {e}")
            logger.error(f"Failed to end MLflow run: {e}")

 