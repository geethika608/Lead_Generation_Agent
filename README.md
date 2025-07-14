# 🤖 Lead Generation Agent

> **AI-Powered Lead Generation System with Multi-Agent Workflow**

A production-grade, scalable AI-powered lead generation system that automates the entire lead generation workflow using CrewAI framework. This system combines multiple specialized AI agents to find, validate, and organize high-quality leads with real-time analytics and monitoring.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-0.141+-green.svg)
![Gradio](https://img.shields.io/badge/Gradio-5.36+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 What This System Does

The Lead Generation Agent is an intelligent system that:

- **🔍 Finds Leads**: Searches LinkedIn and other platforms for potential leads
- **📧 Finds Emails**: Discovers email addresses for each lead
- **✅ Validates Emails**: Checks email deliverability and quality
- **📊 Analyzes Data**: Organizes and stores lead data with insights
- **📈 Tracks Progress**: Provides real-time analytics and monitoring
- **🔗 Integrates**: Saves data to Google Workspace (Sheets & Docs)

## ✨ Key Features

### 🧠 Multi-Agent AI Workflow
- **4 Specialized AI Agents** working together seamlessly
- **Intelligent Task Distribution** for optimal performance
- **Real-time Collaboration** between agents

### 📊 Business Intelligence
- **Real-time Analytics Dashboard** with live metrics
- **Lead Quality Scoring** and performance insights
- **Email Deliverability Analysis** with spam score detection
- **Lead Generation Performance Tracking**

### 🔧 Enterprise Features
- **User Authentication System** with secure login/registration
- **Session Management** with persistent user sessions
- **Google Workspace Integration** for data storage
- **Prometheus Metrics** for monitoring
- **Grafana Dashboards** for visualization
- **DeepEval Evaluation** for AI workflow assessment

### 🎨 User Experience
- **Modern Gradio Interface** with intuitive design
- **Real-time Progress Tracking** with live updates
- **Tabbed Interface** for organized workflow
- **Responsive Design** that works on all devices

## 🏗️ System Architecture

```
Lead Generation Agent
├── 🤖 AI Agents
│   ├── Scraper Agent (Finds leads on LinkedIn)
│   ├── Email Finder Agent (Discovers email addresses)
│   ├── Email Validator Agent (Validates email quality)
│   └── Data Analytics Agent (Organizes and stores data)
├── 🎯 Workflow Engine
│   ├── CrewAI Orchestration
│   ├── Task Management
│   └── Progress Tracking
├── 🖥️ User Interface
│   ├── Gradio Web Interface
│   ├── Authentication System
│   └── Real-time Dashboards
├── 📊 Monitoring & Analytics
│   ├── Prometheus Metrics
│   ├── Grafana Dashboards
│   └── DeepEval Evaluation
└── 🔗 Integrations
    ├── Google Workspace
    ├── OpenAI API
    └── Serper API
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (3.11 or 3.12 recommended)
- **OpenAI API Key** (required)
- **Serper API Key** (optional, for enhanced search)
- **Google Workspace** (optional, for data storage)

### Installation

#### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

1. **Install uv** (if not already installed)
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/lead-generation-agent.git
   cd lead-generation-agent
   ```

3. **Create virtual environment and install dependencies**
   ```bash
   uv sync
   ```

4. **Activate the virtual environment**
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

6. **Configure your API keys**
   ```bash
   # Required
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Optional but recommended
   SERPER_API_KEY=your_serper_api_key_here
   GOOGLE_CREDENTIALS_FILE=path/to/credentials.json
   ```

7. **Launch the application**
   ```bash
   crewai run
   ```

8. **Open your browser**
   Navigate to `http://localhost:7860`

#### Alternative crewai commands
```bash
# Run the main application
crewai run

# Run with specific configuration
crewai run --config path/to/config.yaml

# Run in development mode
crewai run --dev

# Run with custom port
crewai run --port 8080
```

**Note**: The `crewai run` command automatically handles environment setup and launches the Gradio interface.

## 📋 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key for AI agents |
| `SERPER_API_KEY` | ❌ No | Serper API key for enhanced web search |
| `DEEPEVAL_API_KEY` | ❌ No | DeepEval API key for workflow evaluation |
| `GOOGLE_CREDENTIALS_FILE` | ❌ No | Path to Google Workspace credentials |
| `CREWAI_VERBOSE` | ❌ No | Enable verbose logging (true/false) |
| `CREWAI_MAX_RPM` | ❌ No | Maximum requests per minute (default: 5) |

### API Keys Setup

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `.env` file

#### Serper API Key (Optional)
1. Visit [Serper.dev](https://serper.dev)
2. Sign up and get your API key
3. Add it to your `.env` file for enhanced search capabilities

#### Google Workspace Setup (Optional)
See [Google Workspace Setup Guide](docs/GOOGLE_WORKSPACE_SETUP.md) for detailed instructions.

## 🎮 How to Use

### 1. First Time Setup
1. **Register an account** or **login** to the system
2. **Connect your Google account** (optional but recommended)
3. **Configure your API keys** in the settings

### 2. Generate Leads
1. **Navigate to the Lead Generation tab**
2. **Enter your search criteria**:
   - Industry/Company type
   - Job titles or roles
   - Location preferences
   - Company size
3. **Set lead generation parameters**:
   - Number of leads to find
   - Search depth
   - Quality filters

### 3. Monitor Progress
1. **Watch real-time progress** as agents work
2. **View live metrics** and analytics
3. **Track lead quality scores**
4. **Monitor email validation results**

### 4. Export Results
1. **Download results** as CSV/Excel
2. **Save to Google Sheets** (if connected)
3. **Generate reports** with insights
4. **Export to CRM** (coming soon)

## 🤖 AI Agents Explained

### 1. **Scraper Agent** 🔍
- **Purpose**: Finds potential leads on LinkedIn and other platforms
- **Capabilities**: 
  - Searches by industry, job title, company
  - Extracts contact information
  - Filters by location and company size
- **Output**: List of potential leads with basic information

### 2. **Email Finder Agent** 📧
- **Purpose**: Discovers email addresses for each lead
- **Capabilities**:
  - Uses multiple email finding techniques
  - Validates email patterns
  - Checks for common email formats
- **Output**: Email addresses for each lead

### 3. **Email Validator Agent** ✅
- **Purpose**: Validates email quality and deliverability
- **Capabilities**:
  - Checks email syntax and format
  - Validates domain existence
  - Analyzes spam score
  - Tests deliverability
- **Output**: Quality score and validation status

### 4. **Data Analytics Agent** 📊
- **Purpose**: Organizes and analyzes lead data
- **Capabilities**:
  - Categorizes leads by quality
  - Generates insights and reports
  - Stores data in organized format
  - Creates actionable recommendations
- **Output**: Organized data with insights

## 📊 Analytics & Monitoring

### Real-time Metrics
- **Lead Discovery Rate**: How many leads are found per hour
- **Email Validation Success**: Percentage of valid emails
- **Quality Score Distribution**: Breakdown of lead quality
- **Processing Time**: How long each step takes

### Business Intelligence
- **Lead Quality Metrics**: High-quality vs low-quality leads
- **Email Deliverability**: Spam scores and recommendations
- **Lead Generation Performance**: Success rates and efficiency indicators
- **Trend Analysis**: Historical performance data

### Monitoring Tools
- **Prometheus Metrics**: System performance monitoring
- **Grafana Dashboards**: Visual analytics and insights
- **DeepEval Evaluation**: AI workflow assessment
- **Event Listeners**: Modular progress tracking

## 🔧 Advanced Configuration

### Custom Agent Configuration
Edit `src/lead_generation_agent/config/agents.yaml` to customize agent behavior:

```yaml
scraper_agent:
  name: "Lead Scraper"
  role: "Find potential leads on professional networks"
  goals:
    - "Search LinkedIn for target companies and roles"
    - "Extract contact information and company details"
  tools:
    - "serper_search"
    - "linkedin_scraper"
```

### Task Configuration
Modify `src/lead_generation_agent/config/tasks.yaml` to adjust workflow:

```yaml
find_leads:
  description: "Search for potential leads based on criteria"
  agent: "scraper_agent"
  expected_output: "List of potential leads with contact info"
  context: "User has provided search criteria for lead generation"
```

### Monitoring Setup
1. **Prometheus**: Metrics are automatically exposed on `/metrics`
2. **Grafana**: Import dashboards from `monitoring/grafana_dashboards/`
3. **DeepEval**: Configure evaluation metrics in `evaluation/metrics_config.py`

## 🛠️ Development

### Project Structure
```
Lead_Generation_Agent/
├── src/lead_generation_agent/
│   ├── agents/              # Agent configurations
│   ├── config/              # Configuration files
│   ├── evaluation/          # DeepEval evaluation system
│   ├── listeners/           # Event listeners
│   ├── main.py             # Application entry point
│   ├── models/             # Pydantic data models
│   ├── monitoring/         # Prometheus & Grafana
│   ├── services/           # Business logic services
│   ├── tools/              # Custom tools
│   ├── ui/                 # Gradio interface
│   ├── utils/              # Utility functions
│   └── workflows/          # Workflow orchestration
├── docs/                   # Documentation
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
├── uv.lock                 # uv lock file for reproducible builds
└── README.md              # This file
```

### Available Commands

The project includes several convenient commands for different use cases:

```bash
# Main application commands
crewai run                    # Launch the main application
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_agents.py

# Run with coverage
python -m pytest --cov=src/lead_generation_agent tests/

# Run tests with uv
uv run pytest tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🚨 Troubleshooting

### Common Issues

#### 1. **"OPENAI_API_KEY is required"**
- **Solution**: Add your OpenAI API key to the `.env` file
- **Check**: Ensure the key is valid and has sufficient credits

#### 2. **"Module not found" errors**
- **Solution**: Install dependencies with `pip install -r requirements.txt`
- **Check**: Ensure you're in the correct virtual environment

#### 3. **Google Workspace connection issues**
- **Solution**: Follow the [Google Workspace Setup Guide](docs/GOOGLE_WORKSPACE_SETUP.md)
- **Check**: Ensure credentials file path is correct

#### 4. **Slow performance**
- **Solution**: Check your API rate limits
- **Optimization**: Adjust `CREWAI_MAX_RPM` in environment variables

#### 5. **Gradio interface not loading**
- **Solution**: Check if port 7860 is available
- **Alternative**: Change port in `main.py` launch parameters

### Performance Optimization
- **Increase `CREWAI_MAX_RPM`** for faster processing
- **Use Serper API** for enhanced search capabilities
- **Enable verbose logging** for debugging
- **Monitor system resources** during large campaigns

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)**: Detailed installation instructions
- **[Google Workspace Setup](docs/GOOGLE_WORKSPACE_SETUP.md)**: Google integration guide
- **[OAuth2 Flow](docs/GOOGLE_OAUTH2_FLOW.md)**: Authentication details

## 🤝 Support

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/yourusername/lead-generation-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/lead-generation-agent/discussions)
- **Wiki**: [Project Wiki](https://github.com/yourusername/lead-generation-agent/wiki)

### Community
- **Discord**: Join our [Discord Server](https://discord.gg/your-invite)
- **Twitter**: Follow [@YourHandle](https://twitter.com/YourHandle)
- **Blog**: Read our [Blog](https://your-blog.com)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CrewAI Team** for the amazing multi-agent framework
- **OpenAI** for providing the AI capabilities
- **Gradio** for the beautiful web interface
- **All Contributors** who have helped improve this project

## 📈 Roadmap

### Upcoming Features
- [ ] **CRM Integration** (Salesforce, HubSpot, Pipedrive)
- [ ] **Advanced Analytics** with machine learning insights
- [ ] **Email Campaign Automation** with A/B testing
- [ ] **Mobile App** for on-the-go monitoring
- [ ] **API Endpoints** for third-party integrations
- [ ] **Multi-language Support** for global campaigns
- [ ] **Advanced Lead Scoring** with ML models
- [ ] **Team Collaboration** features

### 🚀 Campaign Management Features (Future Scope)

#### 📧 Email Campaign Creation
- **Campaign Builder**: Drag-and-drop email campaign creation interface
- **Template Library**: Pre-built email templates for different industries and use cases
- **Custom Templates**: Create and save personalized email templates
- **Dynamic Content**: Insert lead-specific information (name, company, role) into templates
- **A/B Testing**: Test different subject lines, content, and send times
- **Campaign Scheduling**: Schedule campaigns for optimal delivery times

#### 📨 High-Deliverability Email Sending
- **SMTP Integration**: Connect multiple email providers (Gmail, Outlook, custom SMTP)
- **Email Authentication**: SPF, DKIM, and DMARC setup for better deliverability
- **Warm-up Sequences**: Gradual email volume increase to build sender reputation
- **Bounce Management**: Automatic handling of hard and soft bounces
- **Spam Score Optimization**: AI-powered content optimization to reduce spam scores
- **Rate Limiting**: Intelligent sending rates to avoid being flagged as spam

#### 📊 Campaign Analytics & Tracking
- **Open Rate Tracking**: Monitor email open rates and engagement
- **Click-through Rates**: Track link clicks and user interactions
- **Response Tracking**: Monitor replies and engagement metrics
- **Conversion Tracking**: Track leads through the sales funnel
- **Campaign Performance**: Compare different campaigns and strategies
- **ROI Analytics**: Measure campaign effectiveness and return on investment

#### 🎯 Advanced Campaign Features
- **Segmentation**: Group leads by industry, role, company size, or engagement level
- **Personalization**: AI-powered content personalization based on lead data
- **Follow-up Sequences**: Automated follow-up emails based on engagement
- **Lead Nurturing**: Multi-touch email sequences to nurture prospects
- **Integration with Lead Data**: Seamless connection between generated leads and campaigns
- **Campaign Templates**: Industry-specific campaign templates and best practices

### Version History
- **v0.1.0** - Initial release with core functionality
- **v0.2.0** - Added Google Workspace integration
- **v0.3.0** - Enhanced analytics and monitoring
- **v0.4.0** - Improved UI and user experience

---

**Made with ❤️ by the Lead Generation Agent Team**

*Transform your lead generation with AI-powered automation!* 