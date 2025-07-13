import logging
import re
from typing import Dict, Any, List, Optional
from ..models.analytics_models import WorkflowAnalytics, AgentAnalytics, TaskAnalytics

logger = logging.getLogger(__name__)

class AnalyticsParser:
    """Parser for extracting analytics data from agent outputs"""
    
    def __init__(self):
        self.lead_patterns = [
            r'(\d+)\s+leads?\s+found',
            r'found\s+(\d+)\s+leads?',
            r'(\d+)\s+contacts?\s+found',
            r'found\s+(\d+)\s+contacts?',
            r'total\s+leads?:\s*(\d+)',
            r'leads?:\s*(\d+)',
            r'contacts?:\s*(\d+)'
        ]
    
    def parse_agent_output(self, agent_name: str, output: Any) -> Dict[str, Any]:
        """
        Parse agent output to extract analytics data
        
        Args:
            agent_name: Name of the agent
            output: Agent output data
            
        Returns:
            Dictionary with parsed analytics
        """
        analytics = {
            'leads_found': 0,
            'execution_time': 0.0,
            'success': True,
            'error_message': None
        }
        
        try:
            if isinstance(output, str):
                analytics.update(self._parse_text_output(output))
            elif isinstance(output, dict):
                analytics.update(self._parse_dict_output(output))
            elif isinstance(output, list):
                analytics.update(self._parse_list_output(output))
            elif hasattr(output, 'leads'):
                analytics.update(self._parse_lead_object(output))
            else:
                logger.warning(f"Unknown output type for agent {agent_name}: {type(output)}")
                
        except Exception as e:
            logger.error(f"Error parsing output for agent {agent_name}: {e}")
            analytics['success'] = False
            analytics['error_message'] = str(e)
        
        return analytics
    
    def _parse_text_output(self, text: str) -> Dict[str, Any]:
        """Parse text output to extract analytics"""
        analytics = {'leads_found': 0}
        
        # Extract leads count
        for pattern in self.lead_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    analytics['leads_found'] = int(matches[0])
                    break
                except (ValueError, IndexError):
                    continue
        
        return analytics
    
    def _parse_dict_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse dictionary output to extract analytics"""
        analytics = {'leads_found': 0}
        
        # Extract leads count
        if 'leads_found' in data:
            analytics['leads_found'] = int(data['leads_found'])
        elif 'leads' in data:
            if isinstance(data['leads'], list):
                analytics['leads_found'] = len(data['leads'])
            elif isinstance(data['leads'], dict) and 'leads' in data['leads']:
                analytics['leads_found'] = len(data['leads']['leads'])
        
        # Extract execution time
        if 'execution_time' in data:
            analytics['execution_time'] = float(data['execution_time'])
        
        return analytics
    
    def _parse_list_output(self, data: List[Any]) -> Dict[str, Any]:
        """Parse list output to extract analytics"""
        analytics = {'leads_found': 0}
        
        # If it's a list of leads/contacts
        if len(data) > 0:
            analytics['leads_found'] = len(data)
        
        return analytics
    
    def _parse_lead_object(self, obj: Any) -> Dict[str, Any]:
        """Parse lead object to extract analytics"""
        analytics = {'leads_found': 0}
        
        if hasattr(obj, 'leads') and hasattr(obj.leads, '__len__'):
            analytics['leads_found'] = len(obj.leads)
        
        return analytics
    
    def create_workflow_analytics(self, agent_results: List[Dict[str, Any]], execution_time: float = 0.0) -> WorkflowAnalytics:
        """
        Create workflow analytics from agent results
        
        Args:
            agent_results: List of agent result dictionaries
            execution_time: Total workflow execution time
            
        Returns:
            WorkflowAnalytics object
        """
        total_leads = sum(result.get('leads_found', 0) for result in agent_results)
        success_count = sum(1 for result in agent_results if result.get('success', True))
        total_agents = len(agent_results)
        success_rate = success_count / total_agents if total_agents > 0 else 0.0
        
        return WorkflowAnalytics(
            leads_found=total_leads,
            execution_time=execution_time,
            success_rate=success_rate
        )
    
    def create_agent_analytics(self, agent_name: str, results: List[Dict[str, Any]]) -> AgentAnalytics:
        """
        Create agent analytics from multiple executions
        
        Args:
            agent_name: Name of the agent
            results: List of agent result dictionaries
            
        Returns:
            AgentAnalytics object
        """
        execution_count = len(results)
        execution_time = sum(result.get('execution_time', 0.0) for result in results)
        success_count = sum(1 for result in results if result.get('success', True))
        error_count = execution_count - success_count
        
        return AgentAnalytics(
            agent_name=agent_name,
            execution_count=execution_count,
            execution_time=execution_time,
            success_count=success_count,
            error_count=error_count
        )
    
    def create_task_analytics(self, task_name: str, results: List[Dict[str, Any]]) -> TaskAnalytics:
        """
        Create task analytics from multiple executions
        
        Args:
            task_name: Name of the task
            results: List of task result dictionaries
            
        Returns:
            TaskAnalytics object
        """
        execution_count = len(results)
        execution_time = sum(result.get('execution_time', 0.0) for result in results)
        success_count = sum(1 for result in results if result.get('success', True))
        error_count = execution_count - success_count
        
        return TaskAnalytics(
            task_name=task_name,
            execution_count=execution_count,
            execution_time=execution_time,
            success_count=success_count,
            error_count=error_count
        ) 