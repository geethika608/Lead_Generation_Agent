"""
Lead generation models
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserInput(BaseModel):
    """Model for user input data"""
    search_strategy: str = Field(description="Search strategy for finding leads")
    target_clients: List[str] = Field(description="Target client types")
    campaign_agenda: str = Field(description="Campaign objective")
    max_leads: int = Field(ge=1, le=1000, description="Maximum leads to generate")
    search_depth: int = Field(ge=1, le=5, description="Search depth")

class SearchPlan(BaseModel):
    """Model for search plan data"""
    search_strategy: str = Field(description="Search strategy")
    target_websites: List[str] = Field(description="Target websites to search")
    search_queries: List[str] = Field(description="Search queries to use")
    expected_results: int = Field(description="Expected number of results")

class Lead(BaseModel):
    """Model for lead data"""
    name: str = Field(description="Lead name")
    company: str = Field(description="Company name")
    email: str = Field(description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile")
    position: Optional[str] = Field(None, description="Job position")
    industry: Optional[str] = Field(None, description="Industry")
    location: Optional[str] = Field(None, description="Location")
    source: str = Field(description="Source of the lead")
    confidence_score: float = Field(ge=0, le=1, description="Confidence score")
    scraped_at: datetime = Field(default_factory=datetime.now, description="When lead was scraped")

class LeadList(BaseModel):
    """Model for list of leads"""
    leads: List[Lead] = Field(description="List of leads")
    total_count: int = Field(description="Total number of leads")
    search_queries_used: List[str] = Field(description="Search queries used")
    sources_searched: List[str] = Field(description="Sources that were searched")

class ValidatedLeads(BaseModel):
    """Model for validated leads data"""
    leads: List[Lead] = Field(description="List of validated leads")
    validation_results: List[dict] = Field(description="Email validation results")
    valid_count: int = Field(description="Number of valid emails")
    invalid_count: int = Field(description="Number of invalid emails")
    total_count: int = Field(description="Total number of leads validated")

class CampaignStrategy(BaseModel):
    """Model for campaign strategy data"""
    campaign_name: str = Field(description="Campaign name")
    target_audience: str = Field(description="Target audience description")
    value_proposition: str = Field(description="Value proposition")
    messaging_approach: str = Field(description="Messaging approach")
    call_to_action: str = Field(description="Call to action")
    follow_up_strategy: str = Field(description="Follow-up strategy")
    success_metrics: List[str] = Field(description="Success metrics to track")

 