"""
Agent expectations and sample outputs for DeepEval evaluation
"""

from typing import Dict, Any

# Agent expectations with actual sample outputs based on Pydantic models
AGENT_EXPECTATIONS = {
    'scraper_agent': {
        'description': 'Extracts leads from LinkedIn.com within business domain',
        'expected_outputs': ['leads', 'profiles', 'contact_info'],
        'quality_metrics': ['accuracy', 'relevance', 'completeness']
    },
    'email_validator_agent': {
        'description': 'Validates lead email addresses for quality',
        'expected_outputs': ['validated_leads', 'validation_summary', 'filtered_results'],
        'quality_metrics': ['accuracy', 'completeness', 'filtering_effectiveness']
    },
    'data_analytics_agent': {
        'description': 'Organizes and stores lead data',
        'expected_outputs': ['stored_data', 'file_urls', 'confirmation'],
        'quality_metrics': ['completeness', 'organization', 'accessibility']
    }
}

def get_agent_expectation(agent_name: str) -> Dict[str, Any]:
    """Get expectation for a specific agent"""
    return AGENT_EXPECTATIONS.get(agent_name, {})

def get_sample_output(agent_name: str) -> Dict[str, Any]:
    """Get sample output for a specific agent"""
    expectation = get_agent_expectation(agent_name)
    return expectation.get('sample_output', {})

def get_agent_description(agent_name: str) -> str:
    """Get description for a specific agent"""
    expectation = get_agent_expectation(agent_name)
    return expectation.get('description', 'No description available')

def list_all_agents() -> list:
    """Get list of all agent names"""
    return list(AGENT_EXPECTATIONS.keys()) 