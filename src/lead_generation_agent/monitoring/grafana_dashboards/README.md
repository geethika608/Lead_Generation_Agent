## 📊 Grafana Dashboards

This directory contains pre-configured Grafana dashboard JSON files for monitoring the Lead Generation Agent system.

### 🎯 Dashboard Overview

#### 1. **Agent Workflow Dashboard** (`agent_workflow_dashboard.json`)
**Purpose**: Monitor real-time agent execution, task completion, and workflow progress.

**Key Metrics**:
- Agent execution counts and durations
- Task completion rates and success/failure ratios
- Workflow progress tracking
- Memory usage and performance metrics
- CrewAI framework metrics

#### 2. **Data Analytics Usage Dashboard** (`data_analytics_usage_dashboard.json`)
**Purpose**: Track business metrics, lead generation performance, and campaign analytics.

**Key Metrics**:
- Lead generation counts and quality scores
- Campaign creation and readiness metrics
- Email template generation and spam scores
- Google Workspace integration usage
- Business KPIs and performance indicators

#### 3. **Evaluation Metrics Dashboard** (`evaluation_metrics_dashboard.json`)
**Purpose**: Track evaluation results, quality metrics, and performance trends using DeepEval.

**Key Metrics**:
- Evaluation scores and pass/fail rates
- Agent-specific quality assessments
- Workflow-level evaluation results
- DeepEval metric breakdowns (AnswerRelevancy, Faithfulness, etc.)
- Performance improvement tracking

### 🚀 Setup Instructions

1. **Install Grafana** (if not already installed):
   ```bash
   # Using Docker
   docker run -d -p 3000:3000 grafana/grafana
   
   # Or install locally
   brew install grafana  # macOS
   sudo apt-get install grafana  # Ubuntu
   ```

2. **Access Grafana**:
   - Open http://localhost:3000
   - Default credentials: admin/admin
   - Change password when prompted

3. **Configure Data Source**:
   - Go to Configuration → Data Sources
   - Add Prometheus data source
   - URL: http://localhost:9090
   - Access: Server (default)

4. **Import Dashboards**:
   - Go to Dashboards → Import
   - Upload each JSON file from this directory
   - Select the Prometheus data source
   - Save and view

### 📈 Dashboard Features

#### Real-time Monitoring
- Live updates every 15 seconds
- Color-coded status indicators
- Trend analysis and forecasting
- Alert thresholds and notifications

#### Business Intelligence
- Lead quality scoring
- Campaign effectiveness metrics
- Email deliverability analysis
- ROI and performance tracking

#### Technical Insights
- Agent performance breakdown
- Memory and resource usage
- Error rates and debugging info
- System health monitoring

### 🔧 Customization

#### Adding New Metrics
1. Update Prometheus metrics in `monitoring/prometheus_metrics.py`
2. Modify dashboard JSON files to include new panels
3. Restart the application to collect new metrics

#### Dashboard Modifications
- Edit JSON files to customize panels
- Add new visualizations (graphs, tables, gauges)
- Configure alerts and thresholds
- Set up automated reporting

### 📊 Key Performance Indicators

#### Agent Performance
- Execution time per agent
- Success/failure rates
- Memory usage patterns
- Error frequency and types

#### Business Metrics
- Leads generated per hour/day
- Campaign readiness scores
- Email validation success rates
- Data storage completion rates

#### Evaluation Analytics
- DeepEval score distributions
- Quality improvement trends
- Agent-specific assessments
- Workflow optimization insights

### 🚨 Alerting

Configure alerts in Grafana for:
- Agent failures or timeouts
- Low lead generation rates
- High spam scores
- Evaluation failures
- System resource issues

### 📝 Notes

- Dashboards are optimized for 1920x1080 resolution
- Data retention: 30 days (configurable in Prometheus)
- Refresh rate: 15 seconds (adjustable)
- Export format: PNG, PDF, CSV available 