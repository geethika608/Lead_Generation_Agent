from pydantic import BaseModel, Field
from typing import List

class CampaignStrategy(BaseModel):
    """Model for campaign strategy data"""
    approach: str = Field(description="Overall campaign approach")
    timing: str = Field(description="Campaign timing strategy")
    channels: List[str] = Field(description="Communication channels")
    personalization_tactics: List[str] = Field(description="Personalization strategies")
    target_audience: str = Field(description="Target audience description")

class SearchPlan(BaseModel):
    """Model for search and scraping plan"""
    keywords: List[str] = Field(description="Search keywords")
    target_sites: List[str] = Field(description="Target websites")
    lead_attributes: List[str] = Field(description="Required lead attributes")
    search_depth: int = Field(ge=1, le=5, description="Search depth level") 