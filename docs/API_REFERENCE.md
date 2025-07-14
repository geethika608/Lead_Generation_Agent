# 📚 API Reference

## Overview

This document provides comprehensive API reference for all services, tools, and endpoints in the Lead Generation Agent system.

## 🔧 Core Services

### WorkflowService

The main orchestrator service that manages the entire lead generation workflow.

#### Methods

##### `run_lead_generation()`
```python
def run_lead_generation(
    search_strategy: str,
    target_clients: str,
    campaign_agenda: str,
    max_leads: int,
    search_depth: int,
    session_id: str = None,
    progress_fn=None
) -> str
```

**Parameters:**
- `search_strategy` (str): Search strategy for finding leads
- `target_clients` (str): Comma-separated list of target roles
- `campaign_agenda` (str): Campaign objective
- `max_leads` (int): Maximum number of leads to generate
- `search_depth` (int): Search depth (1-5)
- `session_id` (str, optional): User session ID for authentication
- `progress_fn` (callable, optional): Callback function for progress updates

**Returns:**
- `str`: Formatted string with workflow results

**Example:**
```python
workflow_service = WorkflowService()
result = workflow_service.run_lead_generation(
    search_strategy="site:linkedin.com CTO SaaS",
    target_clients="CTO, VP Engineering",
    campaign_agenda="Book a demo",
    max_leads=50,
    search_depth=3,
    session_id="user_123"
)
```

### EmailService

Service for email validation and spam detection using EmailListVerify API.

#### Methods

##### `validate_single_email()`
```python
def validate_single_email(email: str) -> Dict
```

**Parameters:**
- `email` (str): Email address to validate

**Returns:**
- `Dict`: Validation result with status, deliverability, spam score, etc.

**Example:**
```python
email_service = EmailService()
result = email_service.validate_single_email("john@example.com")
# Returns: {
#     'email': 'john@example.com',
#     'is_valid': True,
#     'deliverability': 'high',
#     'is_spam_trap': False,
#     'score': 85
# }
```

##### `validate_bulk_emails()`
```python
def validate_bulk_emails(emails: List[str]) -> Dict
```

**Parameters:**
- `emails` (List[str]): List of email addresses to validate

**Returns:**
- `Dict`: Bulk validation results with summary statistics

##### `format_validation_result()`
```python
def format_validation_result(email: str, result: Dict) -> str
```

**Parameters:**
- `email` (str): Email address
- `result` (Dict): Validation result

**Returns:**
- `str`: Formatted validation result for display

### ProgressService

Service for tracking real-time progress and state management.

#### Methods

##### `update_progress()`
```python
def update_progress(
    stage: str,
    message: str,
    percentage: float = None,
    data: Dict = None
)
```

**Parameters:**
- `stage` (str): Current workflow stage
- `message` (str): Progress message
- `percentage` (float, optional): Completion percentage
- `data` (Dict, optional): Additional data

##### `get_live_progress()`
```python
def get_live_progress() -> str
```

**Returns:**
- `str`: Current progress status

##### `get_evaluation_results()`
```python
def get_evaluation_results() -> Dict
```

**Returns:**
- `Dict`: Evaluation results if available

### AnalyticsService

Service for data analysis and insights generation.

#### Methods

##### `analyze_lead_data()`
```python
def analyze_lead_data(leads: List[Dict]) -> Dict
```

**Parameters:**
- `leads` (List[Dict]): List of lead data

**Returns:**
- `Dict`: Analysis results with insights and metrics

##### `generate_report()`
```python
def generate_report(analysis_data: Dict) -> str
```

**Parameters:**
- `analysis_data` (Dict): Analysis data

**Returns:**
- `str`: Formatted report

## 🛠️ Tools

### Email Validator Tool

Tool for validating email addresses using EmailListVerify API.

#### Usage
```python
@tool("email_validator")
def validate_email(emails: str) -> str
```

**Parameters:**
- `emails` (str): JSON string of email addresses for validation

**Example:**
```json
{
    "emails": "[\"john@example.com\", \"jane@example.com\"]"
}
```

**Returns:**
- `str`: Formatted validation results

### Google Sheets Tool

Tool for saving data to Google Sheets.

#### Usage
```python
@tool("google_sheets_saver")
def save_to_google_sheets(
    data: str,
    sheet_name: str = "Leads",
    user_id: str = "default"
) -> str
```

**Parameters:**
- `data` (str): JSON string of data to save
- `sheet_name` (str): Name of the sheet
- `user_id` (str): User ID for authentication

**Example:**
```json
{
    "data": "[{\"name\": \"John Doe\", \"email\": \"john@example.com\"}]",
    "sheet_name": "Leads",
    "user_id": "user_123"
}
```

**Returns:**
- `str`: Success message with spreadsheet URL

### Google Docs Tool

Tool for saving reports to Google Docs.

#### Usage
```python
@tool("google_docs_saver")
def save_to_google_docs(
    content: str,
    document_title: str = "Campaign Report",
    user_id: Optional[str] = None
) -> str
```

**Parameters:**
- `content` (str): Content to save to the document
- `document_title` (str): Title for the new document
- `user_id` (str, optional): User ID for authentication

## 🤖 AI Agents

### Scraper Agent

Agent responsible for finding leads on LinkedIn and other platforms.

#### Configuration
```yaml
scraper_agent:
  role: "Lead Scraper"
  goal: "Find potential leads on professional networks"
  backstory: "Expert at searching LinkedIn and extracting contact information"
  max_rpm: 100
  max_iter: 50
  llm: openai/gpt-4o-mini
```

#### Tools
- `SerperDevTool`: Web search capabilities

#### Output
- `LeadList`: JSON array of lead objects

### Email Finder Agent

Agent responsible for discovering email addresses for leads.

#### Configuration
```yaml
email_finder_agent:
  role: "Email Address Finder"
  goal: "Find email addresses for leads using multiple search strategies"
  backstory: "Expert email researcher with deep knowledge of various online sources"
  max_rpm: 100
  max_iter: 50
  llm: openai/gpt-4o-mini
```

#### Tools
- `SerperDevTool`: Web search capabilities

#### Output
- `LeadList`: JSON array of leads with email addresses

### Email Validator Agent

Agent responsible for validating email quality and deliverability.

#### Configuration
```yaml
email_validator_agent:
  role: "Lead Email Validator"
  goal: "Validate and filter lead email addresses for deliverability"
  backstory: "Email deliverability specialist with expertise in validation APIs"
  max_rpm: 2
  max_iter: 2
  llm: openai/gpt-4.1-nano
```

#### Tools
- `validate_email`: Email validation tool

#### Output
- `ValidatedLeads`: JSON object with validated leads and summary

### Data Analytics Agent

Agent responsible for organizing and analyzing lead data.

#### Configuration
```yaml
data_analytics_agent:
  role: "Data Analytics Specialist"
  goal: "Organize and analyze lead data for insights"
  backstory: "Expert at data processing and generating actionable insights"
  max_rpm: 50
  max_iter: 25
  llm: openai/gpt-4o-mini
```

#### Tools
- `save_to_google_sheets`: Data export tool

## 📊 Data Models

### Lead Model
```python
class Lead(BaseModel):
    name: str
    email: str
    company: str
    title: str
    linkedin: Optional[str] = None
    validation_status: Optional[str] = None
```

### ValidatedLeads Model
```python
class ValidatedLeads(BaseModel):
    leads: List[Lead]
    validation_summary: Dict[str, Any]
    quality_metrics: Dict[str, Any]
```

### UserInput Model
```python
class UserInput(BaseModel):
    search_strategy: str
    target_clients: List[str]
    campaign_agenda: str
    max_leads: int
    search_depth: int
```

### LeadList Model
```python
class LeadList(BaseModel):
    leads: List[Lead]
```

## 🔌 Integration APIs

### EmailListVerify API

#### Endpoint
```
GET https://apps.emaillistverify.com/api/verifyEmail
```

#### Parameters
- `secret`: API key
- `email`: Email address to validate

#### Response
```json
{
    "status": "success",
    "deliverability": "high",
    "spam_trap": false,
    "disposable": false,
    "catch_all": false,
    "syntax_error": false,
    "score": 85
}
```

### Google Workspace APIs

#### Google Sheets API
- **Create Spreadsheet**: `POST /spreadsheets`
- **Update Values**: `PUT /spreadsheets/{spreadsheetId}/values/{range}`
- **Get Values**: `GET /spreadsheets/{spreadsheetId}/values/{range}`

#### Google Docs API
- **Create Document**: `POST /documents`
- **Update Document**: `PATCH /documents/{documentId}`
- **Get Document**: `GET /documents/{documentId}`

## 📈 Monitoring APIs

### Prometheus Metrics

#### Workflow Metrics
- `workflow_start_total`: Total workflow starts
- `workflow_completion_duration_seconds`: Workflow completion time
- `workflow_success_total`: Successful workflow completions
- `workflow_failure_total`: Failed workflow completions

#### Lead Metrics
- `leads_found_total`: Total leads found
- `leads_validated_total`: Total leads validated
- `email_validation_success_rate`: Email validation success rate

#### Agent Metrics
- `agent_execution_duration_seconds`: Agent execution time
- `agent_success_total`: Successful agent executions
- `agent_failure_total`: Failed agent executions

### Grafana Dashboards

#### Available Dashboards
- **Agent Workflow Dashboard**: Real-time agent performance
- **Data Analytics Usage Dashboard**: Analytics and insights
- **Evaluation Metrics Dashboard**: AI evaluation results

## 🔒 Authentication

### Session Management

#### Session Creation
```python
session_service.create_session(user_data: Dict) -> str
```

#### Session Validation
```python
session_service.get_session(session_id: str) -> Dict
```

#### Session Cleanup
```python
session_service.delete_session(session_id: str)
```

### Google OAuth2

#### Authentication Flow
1. **Authorization Request**: Redirect to Google OAuth2 endpoint
2. **Authorization Code**: Receive authorization code
3. **Token Exchange**: Exchange code for access token
4. **Token Storage**: Store tokens securely
5. **API Access**: Use tokens for Google Workspace APIs

#### Token Management
```python
# Token refresh
google_auth.refresh_tokens(refresh_token: str) -> Dict

# Token validation
google_auth.validate_tokens(access_token: str) -> bool

# Token cleanup
google_auth.clear_tokens(user_id: str)
```

## 🚨 Error Handling

### Common Error Codes

#### API Errors
- `400`: Bad Request - Invalid input parameters
- `401`: Unauthorized - Missing or invalid authentication
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server-side error

#### Workflow Errors
- `WORKFLOW_INITIALIZATION_ERROR`: Failed to initialize workflow
- `AGENT_EXECUTION_ERROR`: Agent execution failed
- `DATA_VALIDATION_ERROR`: Data validation failed
- `EXTERNAL_API_ERROR`: External API call failed
- `STORAGE_ERROR`: Data storage operation failed

### Error Response Format
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable error message",
        "details": "Additional error details",
        "timestamp": "2024-01-01T00:00:00Z"
    }
}
```

## 📝 Usage Examples

### Complete Workflow Example
```python
from src.lead_generation_agent.services.workflow_service import WorkflowService

# Initialize service
workflow_service = WorkflowService()

# Run lead generation
result = workflow_service.run_lead_generation(
    search_strategy="site:linkedin.com CTO SaaS companies",
    target_clients="CTO, VP Engineering, Technical Director",
    campaign_agenda="Schedule a product demo",
    max_leads=100,
    search_depth=4,
    session_id="user_session_123"
)

print(result)
```

### Email Validation Example
```python
from src.lead_generation_agent.services.email_service import EmailService

# Initialize service
email_service = EmailService()

# Validate single email
result = email_service.validate_single_email("john@example.com")
print(email_service.format_validation_result("john@example.com", result))

# Validate bulk emails
emails = ["john@example.com", "jane@example.com", "bob@example.com"]
bulk_result = email_service.validate_bulk_emails(emails)
print(email_service.format_bulk_validation_result(bulk_result))
```

### Google Integration Example
```python
from src.lead_generation_agent.tools.google_sheets import save_to_google_sheets

# Save data to Google Sheets
data = [
    {"name": "John Doe", "email": "john@example.com", "company": "Tech Corp"},
    {"name": "Jane Smith", "email": "jane@example.com", "company": "Startup Inc"}
]

result = save_to_google_sheets(
    data=json.dumps(data),
    sheet_name="Leads",
    user_id="user_123"
)
print(result)
```

This API reference provides comprehensive documentation for all system components, enabling developers to understand and integrate with the Lead Generation Agent system effectively. 