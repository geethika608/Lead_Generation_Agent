# Lead Generation Agent

A production-grade, scalable AI-powered lead generation system built with CrewAI framework. This system automates the entire lead generation workflow from user input collection to campaign execution with real-time analytics and monitoring.

## 🚀 Features

### Core Functionality
- **Multi-Agent Workflow**: 4 specialized AI agents working together
- **Real-time Progress Tracking**: Live updates on workflow progress and business metrics
- **Business Analytics**: Lead quality metrics and performance insights
- **Email Validation**: Built-in deliverability analysis
- **Google Workspace Integration**: Save data to Sheets and Docs
- **Modular Architecture**: Clean separation of concerns with Pydantic models

### Agents
1. **Scraper Agent**: Finds leads using SerperDev search on LinkedIn
2. **Email Finder Agent**: Finds email addresses for leads
3. **Email Validator Agent**: Validates email addresses for quality
4. **Data Analytics Agent**: Organizes and stores campaign data

### Monitoring & Evaluation
- **Prometheus Metrics**: Real-time performance monitoring
- **Grafana Dashboards**: Visual analytics and insights
- **DeepEval Evaluation**: AI-powered workflow assessment with multiple metrics
- **Event Listeners**: Modular progress tracking system

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key (required)
- Serper API key (optional, for enhanced search)
- Google Workspace credentials (optional, for data storage)
- DeepEval (optional, for evaluation)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Lead_Generation_Agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## 🔧 Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Optional Environment Variables
```bash
SERPER_API_KEY=your_serper_api_key_here
DEEPEVAL_API_KEY=your_deepeval_api_key_here
GOOGLE_CREDENTIALS_FILE=credentials.json
```

## 🚀 Usage

### Launch the Application
```bash
python main.py
```
Then open http://localhost:7860 in your browser.

The application will automatically launch the Gradio UI interface where you can:
- Configure your lead generation campaign
- Connect your Google account for data storage
- Monitor real-time progress and analytics
- View comprehensive reports

## 📊 Business Analytics

The system provides real-time business metrics:

- **Lead Quality Metrics**: Number of high-quality leads found
- **Email Deliverability**: Spam scores and recommendations
- **Performance Tracking**: Execution time and success rates

## 🏗️ Architecture

```
Lead_Generation_Agent/
├── agents/                 # Agent configurations (YAML-based)
├── config/                 # Configuration files
│   ├── agents.yaml        # Agent definitions
│   ├── tasks.yaml         # Task definitions
│   └── default_config.yaml # Default settings
├── crew.py                # Main CrewAI orchestration
├── models/                # Pydantic data models
├── tools/                 # Custom tools
├── listeners/             # Event listeners for progress tracking
├── workflows/             # Workflow orchestration
├── ui/                    # Gradio interface
├── monitoring/            # Prometheus metrics and Grafana dashboards
└── evaluation/            # DeepEval evaluation system
```

## 🔄 Workflow

1. **User Input Collection**: Gather campaign requirements
2. **Lead Generation Planning**: Create search strategy
3. **Lead Scraping**: Find and extract leads
4. **Campaign Strategy**: Develop outreach approach
5. **Email Creation**: Generate templates 