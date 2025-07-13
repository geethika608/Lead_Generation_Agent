"""
Models package for lead generation agent
"""

from .lead_models import (
    UserInput, SearchPlan, Lead, LeadList, ValidatedLeads,
    CampaignStrategy
)

from .campaign_models import (
    CampaignStrategy as CampaignStrategyModel, SearchPlan as SearchPlanModel
)



from .user_models import (
    User, UserLogin, UserRegistration, UserProfile, UserRole, UserStatus, PasswordChange
)

from .analytics_models import (
    WorkflowAnalytics, AgentExecutionRecord
)

__all__ = [
    # Lead models
    'UserInput',
    'SearchPlan', 
    'Lead',
    'LeadList',
    'ValidatedLeads',
    'CampaignStrategy',

    
    # Campaign models
    'CampaignStrategyModel',
    'SearchPlanModel',
    

    
    # User models
    'User',
    'UserLogin',
    'UserRegistration',
    'UserProfile',
    'UserRole',
    'UserStatus',
    'PasswordChange',
    
    # Analytics models
    'WorkflowAnalytics',
    'AgentExecutionRecord'
] 