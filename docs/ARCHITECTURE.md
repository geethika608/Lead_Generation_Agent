# 🏗️ System Architecture

## Overview

The Lead Generation Agent is built using a **multi-agent AI architecture** powered by CrewAI framework, designed for scalability, maintainability, and extensibility. The system follows a **microservices-inspired** approach with clear separation of concerns.

## 🏛️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  Gradio Web UI  │  Authentication  │  Session Management       │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Workflow Service  │  Progress Service  │  Analytics Service    │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                        AI Agent Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Scraper Agent  │  Email Finder  │  Email Validator  │  Analytics │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Integration Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Google Workspace  │  Email APIs  │  Search APIs  │  Monitoring  │
└─────────────────────────────────────────────────────────────────┘
```

## 🧩 Core Components

### 1. **Multi-Agent AI System**

#### Agent Architecture
```yaml
LeadGenerationCrew:
  agents:
    - scraper_agent: LinkedIn and web scraping
    - email_finder_agent: Email discovery
    - email_validator_agent: Email validation
    - data_analytics_agent: Data processing
  memory:
    - long_term_memory: SQLite-based persistent storage
    - short_term_memory: RAG-based temporary storage
    - entity_memory: Entity-focused storage
```

#### Agent Communication Flow
```
User Input → Scraper Agent → Email Finder → Email Validator → Analytics → Output
     ↓           ↓              ↓              ↓              ↓
  Progress   Lead Data    Email Data    Validation    Final Results
  Tracking   Collection   Discovery     Results       & Reports
```

### 2. **Service Layer Architecture**

#### Service Responsibilities
- **WorkflowService**: Orchestrates the entire lead generation process
- **ProgressService**: Tracks real-time progress and state management
- **AnalyticsService**: Handles data analysis and insights generation
- **EmailService**: Manages email validation and deliverability checks
- **SessionService**: Handles user authentication and session management
- **DatabaseService**: Manages data persistence and retrieval

#### Service Communication Pattern
```python
# Example: Service interaction
workflow_service = WorkflowService()
workflow_service.run_lead_generation(
    search_strategy="...",
    target_clients="...",
    campaign_agenda="...",
    max_leads=50,
    search_depth=3,
    session_id="user_session_123"
)
```

### 3. **Data Flow Architecture**

#### Lead Generation Pipeline
```
1. User Input Validation
   ↓
2. Lead Discovery (Scraper Agent)
   ↓
3. Email Discovery (Email Finder Agent)
   ↓
4. Email Validation (Email Validator Agent)
   ↓
5. Data Analysis (Analytics Agent)
   ↓
6. Results Export (Google Sheets/Docs)
```

#### Data Models
```python
# Core data structures
Lead:
  - name: str
  - email: str
  - company: str
  - title: str
  - linkedin: str
  - validation_status: str

ValidatedLeads:
  - leads: List[Lead]
  - validation_summary: Dict
  - quality_metrics: Dict

UserInput:
  - search_strategy: str
  - target_clients: List[str]
  - campaign_agenda: str
  - max_leads: int
  - search_depth: int
```

## 🔧 Technical Implementation

### 1. **Framework Stack**

#### Core Technologies
- **CrewAI**: Multi-agent AI orchestration framework
- **Gradio**: Web interface and user experience
- **FastAPI**: Backend API and service layer
- **Pydantic**: Data validation and serialization
- **SQLite**: Local data persistence
- **Prometheus**: Metrics collection and monitoring

#### AI/ML Stack
- **OpenAI GPT-4**: Primary language model for agents
- **OpenAI Embeddings**: Vector embeddings for memory
- **DeepEval**: AI workflow evaluation and testing
- **MLflow**: Experiment tracking and model management

### 2. **Memory Management**

#### Memory Architecture
```python
# Memory configuration
LongTermMemory:
  storage: LTMSQLiteStorage
  purpose: Persistent knowledge storage
  retention: Permanent

ShortTermMemory:
  storage: RAGStorage
  purpose: Temporary workflow context
  retention: Session-based

EntityMemory:
  storage: RAGStorage
  purpose: Entity-focused information
  retention: Configurable
```

#### Memory Usage Patterns
- **Long-term**: Stores learned patterns, user preferences, historical data
- **Short-term**: Maintains workflow context, agent communication
- **Entity**: Focuses on specific entities (leads, companies, users)

### 3. **Integration Architecture**

#### External API Integration
```python
# API integration pattern
class EmailService:
    def __init__(self):
        self.api_key = os.getenv('EMAILLISTVERIFY_API_KEY')
        self.base_url = "https://apps.emaillistverify.com/api/verifyEmail"
    
    def validate_single_email(self, email: str) -> Dict:
        # API call implementation
        pass
```

#### Google Workspace Integration
- **OAuth2 Flow**: Secure authentication
- **Sheets API**: Data export and storage
- **Docs API**: Report generation
- **User-specific**: Isolated data per user

### 4. **Monitoring & Observability**

#### Metrics Collection
```python
# Prometheus metrics
record_workflow_start()
record_workflow_completion(duration=execution_time, success=True)
record_lead_analytics(found=leads_found)
record_evaluation_result(score=evaluation_score)
```

#### Monitoring Stack
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Custom Metrics**: Workflow-specific KPIs
- **Event Listeners**: Real-time progress tracking

## 🚀 Scalability Considerations

### 1. **Horizontal Scaling**
- **Stateless Services**: All services are stateless for easy scaling
- **Database Sharding**: SQLite can be replaced with distributed databases
- **Load Balancing**: Multiple instances can be deployed behind a load balancer

### 2. **Performance Optimization**
- **Async Processing**: Non-blocking operations for better responsiveness
- **Caching**: Memory-based caching for frequently accessed data
- **Rate Limiting**: API rate limiting to prevent abuse
- **Batch Processing**: Bulk operations for efficiency

### 3. **Resource Management**
- **Memory Optimization**: Efficient memory usage patterns
- **API Quota Management**: Intelligent API usage to stay within limits
- **Error Handling**: Graceful degradation and recovery

## 🔒 Security Architecture

### 1. **Authentication & Authorization**
- **Session-based**: Secure session management
- **OAuth2**: Google Workspace integration
- **API Key Management**: Secure storage of external API keys
- **User Isolation**: Data isolation between users

### 2. **Data Security**
- **Environment Variables**: Sensitive data stored in environment variables
- **Input Validation**: Comprehensive input sanitization
- **Output Sanitization**: Safe data output handling
- **Audit Logging**: Security event tracking

### 3. **API Security**
- **Rate Limiting**: Prevent API abuse
- **Input Validation**: Validate all external inputs
- **Error Handling**: Secure error messages
- **CORS Configuration**: Proper cross-origin resource sharing

## 📊 Data Architecture

### 1. **Data Storage**
```
Local Storage:
├── SQLite Database (long-term memory)
├── RAG Storage (short-term memory)
├── File System (output files)
└── Environment Variables (configuration)

Cloud Storage:
├── Google Sheets (user data)
├── Google Docs (reports)
└── MLflow (experiment tracking)
```

### 2. **Data Flow**
```
Input Data → Validation → Processing → Storage → Export
     ↓           ↓           ↓          ↓        ↓
  User Input  Pydantic   AI Agents   SQLite   Google
  Forms       Models     Processing  Storage   Workspace
```

### 3. **Data Models**
```python
# Core data models
class Lead(BaseModel):
    name: str
    email: str
    company: str
    title: str
    linkedin: Optional[str] = None
    validation_status: Optional[str] = None

class UserInput(BaseModel):
    search_strategy: str
    target_clients: List[str]
    campaign_agenda: str
    max_leads: int
    search_depth: int
```

## 🔄 Deployment Architecture

### 1. **Development Environment**
```
Local Development:
├── Python Virtual Environment
├── Local SQLite Database
├── Local File Storage
└── Development API Keys
```

### 2. **Production Considerations**
```
Production Deployment:
├── Container Orchestration (Docker/Kubernetes)
├── Distributed Database (PostgreSQL/MongoDB)
├── Cloud Storage (AWS S3/GCP Storage)
├── Load Balancer
└── Monitoring Stack (Prometheus/Grafana)
```

### 3. **Configuration Management**
```python
# Configuration hierarchy
1. Environment Variables (highest priority)
2. Configuration Files (YAML/JSON)
3. Default Values (lowest priority)
```

## 🧪 Testing Architecture

### 1. **Testing Strategy**
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **End-to-End Tests**: Complete workflow testing
- **AI Evaluation**: DeepEval-based AI workflow testing

### 2. **Test Coverage**
```
Test Coverage Areas:
├── Agent Logic (90%+)
├── Service Layer (85%+)
├── API Endpoints (80%+)
├── UI Components (75%+)
└── Integration Points (70%+)
```

## 📈 Performance Metrics

### 1. **Key Performance Indicators**
- **Lead Generation Rate**: Leads per hour
- **Email Validation Accuracy**: Percentage of correct validations
- **Workflow Completion Time**: End-to-end processing time
- **User Satisfaction**: Response time and success rate

### 2. **Monitoring Dashboards**
- **Agent Performance**: Individual agent metrics
- **System Health**: Overall system status
- **User Analytics**: Usage patterns and trends
- **Error Tracking**: Issue identification and resolution

This architecture provides a solid foundation for the current lead generation capabilities while maintaining flexibility for future enhancements and scaling requirements. 