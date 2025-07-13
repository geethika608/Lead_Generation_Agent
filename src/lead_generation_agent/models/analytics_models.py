from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class WorkflowAnalytics(BaseModel):
    """Analytics data for workflow execution"""
    leads_found: int = Field(default=0, description="Number of leads found")
    execution_time: float = Field(default=0.0, description="Workflow execution time in seconds")
    evaluation_score: Optional[float] = Field(default=None, description="Workflow evaluation score")
    success_rate: float = Field(default=0.0, description="Overall success rate")
    created_at: datetime = Field(default_factory=datetime.now, description="When analytics were created")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AgentExecutionRecord(BaseModel):
    """Model for agent execution records"""
    agent_name: str = Field(description="Name of the agent")
    task_name: str = Field(description="Task being performed")
    output_data: Any = Field(description="Agent output data")
    success: bool = Field(description="Whether the task was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_time: Optional[float] = Field(None, description="Task execution time in seconds")
    
    def extract_analytics(self) -> WorkflowAnalytics:
        """Extract analytics from agent output data"""
        analytics = WorkflowAnalytics()
        if not self.success or not self.output_data:
            return analytics
        output = self.output_data
        if isinstance(output, str):
            output_lower = output.lower()
            if 'lead' in output_lower or 'contact' in output_lower:
                analytics.leads_found = 1
        elif isinstance(output, dict):
            analytics.leads_found = output.get('leads_found', 0)
        elif isinstance(output, list):
            if len(output) > 0:
                analytics.leads_found = len(output)
        elif hasattr(output, 'leads') and hasattr(output, '__len__'):
            analytics.leads_found = len(output.leads)
        return analytics

class AgentAnalytics(BaseModel):
    """Analytics data for individual agent execution"""
    agent_name: str = Field(description="Name of the agent")
    execution_count: int = Field(default=0, description="Number of times agent was executed")
    execution_time: float = Field(default=0.0, description="Total execution time in seconds")
    success_count: int = Field(default=0, description="Number of successful executions")
    error_count: int = Field(default=0, description="Number of failed executions")
    created_at: datetime = Field(default_factory=datetime.now, description="When analytics were created")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TaskAnalytics(BaseModel):
    """Analytics data for individual task execution"""
    task_name: str = Field(description="Name of the task")
    execution_count: int = Field(default=0, description="Number of times task was executed")
    execution_time: float = Field(default=0.0, description="Total execution time in seconds")
    success_count: int = Field(default=0, description="Number of successful executions")
    error_count: int = Field(default=0, description="Number of failed executions")
    created_at: datetime = Field(default_factory=datetime.now, description="When analytics were created")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AnalyticsSummary(BaseModel):
    """Summary of all analytics data"""
    workflow_analytics: WorkflowAnalytics = Field(description="Workflow-level analytics")
    agent_analytics: List[AgentAnalytics] = Field(default_factory=list, description="Agent-level analytics")
    task_analytics: List[TaskAnalytics] = Field(default_factory=list, description="Task-level analytics")
    created_at: datetime = Field(default_factory=datetime.now, description="When summary was created")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 