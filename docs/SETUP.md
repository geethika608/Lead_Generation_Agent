# Lead Generation Agent Setup Guide

## Overview

The Lead Generation Agent is a comprehensive AI-powered system for automated lead generation and campaign management. It features a modular architecture with multiple AI agents, Google Workspace integration, real-time monitoring, and a modern web interface.

## Architecture

The system follows a clean service-oriented architecture:

### **Services Layer** (`services/`)
- **AuthService**: User authentication, session management, Google OAuth2
- **EmailService**: Email validation, spam detection, bulk processing
- **ProgressService**: Workflow progress tracking, analytics display
- **WorkflowService**: Workflow execution, input validation, result formatting
- **AnalyticsService**: Campaign analytics, reporting, metrics calculation

### **UI Components** (`ui/components/`)
- **InterfaceBuilder**: UI layout and form components
- **ProgressTracker**: Progress display components
- **WorkflowRunner**: Workflow execution UI
- **AuthComponents**: Authentication UI components
- **GoogleAuthComponents**: Google integration UI
- **InputValidator**: Input validation UI logic

### **Core Components**
- **CrewAI Agents**: AI agents for lead generation tasks
- **Tools**: External integrations (Google Workspace, EmailListVerify)
- **Models**: Pydantic data models for type safety
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Evaluation**: DeepEval integration for performance assessment

## Features

- 🤖 **Multi-Agent AI System**: Scraper, email finder, email validator, and data analytics agents
- 🔐 **User Authentication**: Secure login/registration system with session management
- 👤 **User Profiles**: Individual user accounts with profile management
- 🔗 **Google Workspace Integration**: OAuth2 authentication for Google Sheets and Docs
- 📊 **Real-time Monitoring**: Prometheus metrics and Grafana dashboards
- 📈 **Performance Evaluation**: DeepEval integration for agent and workflow evaluation
- 🎯 **Email Validation**: Integration with EmailListVerify API
- 🛡️ **Spam Detection**: Email content analysis and spam scoring
- 📱 **Modern UI**: Gradio-based interface with real-time progress tracking

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- EmailListVerify API key (optional, for email validation)
- Google Workspace credentials (optional, for Google integration)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Lead_Generation_Agent
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```

5. **Configure your `.env` file**:
   ```env
   # Required
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Optional - Email validation
   EMAILLISTVERIFY_API_KEY=your_emaillistverify_api_key_here
   
   # Optional - Google Workspace integration
   GOOGLE_CREDENTIALS_FILE=path/to/your/credentials.json
   ```

## Google Workspace Setup

For Google Sheets and Docs integration, follow the [Google Workspace Setup Guide](GOOGLE_WORKSPACE_SETUP.md).

## Authentication System

The application includes a comprehensive authentication system:

### User Registration
- Username (3+ characters, alphanumeric only)
- Email address
- Strong password (8+ characters, uppercase, lowercase, digit)
- Optional profile information (first name, last name, company)

### User Login
- Login with username or email
- Remember me functionality (30-day sessions)
- Secure password verification

### User Profiles
- Profile information management
- Google account integration
- Password change functionality
- Account status tracking

### Session Management
- Secure session tokens
- Automatic session expiration
- Multi-user support with isolated data

## Usage

### Starting the Application

1. **Launch the UI**:
   ```bash
   python main.py
   ```

2. **Access the interface**:
   - Open your browser to `http://localhost:7860`
   - Register a new account or login with existing credentials
   - Navigate through the tabs: Login, Register, Lead Generation, Profile

### Using the Lead Generation System

1. **Authentication**:
   - Register a new account or login
   - Optionally connect your Google account for data export

2. **Lead Generation**:
   - Enter your business domain
   - Specify target client types
   - Define campaign objectives
   - Set lead generation parameters
   - Run the workflow

3. **Monitoring Progress**:
   - Real-time progress tracking
   - Agent status updates
   - Workflow completion notifications

4. **Results and Export**:
   - View generated leads
   - Export to Google Sheets/Docs
   - Access evaluation metrics

## Configuration

### Agent Configuration

Edit `config/agents.yaml` to customize agent behavior:

```yaml
user_input_agent:
  name: "User Input Agent"
  role: "Collects and validates user requirements"
  goal: "Gather comprehensive user input for lead generation"
  backstory: "Expert at understanding business needs and requirements"
  verbose: true
  allow_delegation: false
  tools: []
```

### Task Configuration

Edit `config/tasks.yaml` to customize task definitions:

```yaml
collect_user_input:
  description: "Collect and validate user input for lead generation"
  expected_output: "Validated user input with business requirements"
  agent: "user_input_agent"
  context: "User provides business domain, target clients, and campaign objectives"
```

### Default Configuration

Edit `config/default_config.yaml` for system-wide settings:

```yaml
# OpenAI Configuration
openai:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 4000

# Email Validation
email_validation:
  enabled: true
  api_key: "${EMAILLISTVERIFY_API_KEY}"

# Google Workspace
google_workspace:
  enabled: true
  credentials_file: "${GOOGLE_CREDENTIALS_FILE}"
```

## Monitoring and Evaluation

### Prometheus Metrics

The system automatically collects metrics for:
- Agent performance and execution times
- Task completion rates
- Workflow success rates
- Email validation statistics
- Lead generation analytics

### Grafana Dashboards

Pre-configured dashboards are available in `monitoring/grafana_dashboards/`:
- Agent Workflow Dashboard
- Data Analytics Usage Dashboard
- Evaluation Metrics Dashboard

### DeepEval Integration

Automatic evaluation of:
- Agent performance against expectations
- Workflow completion quality
- Output validation and scoring
- Comprehensive feedback generation

## Testing

### Authentication System Test

Test the complete authentication system:

```bash
python test_auth_system.py
```

### Multi-User Google Authentication Test

Test Google Workspace integration with multiple users:

```bash
python test_multi_user_auth.py
```

### DeepEval Test

Test the evaluation system:

```bash
python test_deepeval_integration.py
```

## File Structure

```
Lead_Generation_Agent/
├── config/                 # Configuration files
├── docs/                   # Documentation
├── evaluation/             # DeepEval evaluation system
├── listeners/              # Event handlers and state management
├── models/                 # Pydantic data models
├── monitoring/             # Prometheus metrics and Grafana dashboards
├── services/               # Business logic services
│   ├── auth_service.py     # Authentication and user management
│   ├── email_service.py    # Email validation and spam detection
│   ├── progress_service.py # Progress tracking and analytics
│   ├── workflow_service.py # Workflow execution and management
│   └── analytics_service.py # Campaign analytics and reporting
├── tools/                  # Custom tools and integrations
├── ui/                     # Gradio interface components
│   └── components/         # UI component modules
├── workflows/              # Workflow definitions
├── crew.py                 # Main CrewAI crew definition
├── main.py                # Main entry point
└── requirements.txt       # Python dependencies
```