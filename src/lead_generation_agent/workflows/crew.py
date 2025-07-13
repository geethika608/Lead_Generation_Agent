import os
from datetime import datetime
from crewai import Crew, Agent, Task
from crewai.project import CrewBase, agent, task, crew
from crewai.process import Process
from crewai.utilities.events import crewai_event_bus
from ..monitoring.prometheus_metrics import get_metrics_app
from dotenv import load_dotenv
from crewai_tools import SerperDevTool
from ..tools.email_validator import validate_email
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from ..listeners.ui_progress_listener import ui_progress_listener
from ..models import UserInput, Lead, ValidatedLeads, LeadList
from pathlib import Path
from ..tools.google_sheets import save_to_google_sheets

# Load environment variables
load_dotenv()

# Ensure memory directories exist
def ensure_memory_directories():
    """Create memory directories if they don't exist"""
    directories = [
        "memory",
        "memory/long_term",
        "memory/short_term", 
        "memory/entity"
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Create directories
ensure_memory_directories()

@CrewBase
class LeadGenerationCrew:
    """Lead Generation crew for automated lead generation and campaign management"""

    agents_config = '../config/agents.yaml'
    tasks_config = '../config/tasks.yaml'

    def __init__(self):
        """Initialize crew"""
        self.long_term_memory = LongTermMemory(
            storage=LTMSQLiteStorage(db_path="./memory/long_term.db")
        )
        self.short_term_memory = ShortTermMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai",
                    "config": {"model": "text-embedding-3-small"}
                },
                type="short_term",
                path="./memory/short_term"
            )
        )
        self.entity_memory = EntityMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai",
                    "config": {"model": "text-embedding-3-small"}
                },
                type="entity",
                path="./memory/entity"
            )
        )
    
    @agent
    def scraper_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['scraper_agent'],
            tools=[SerperDevTool()],
            output_pydantic=LeadList,
        )
    
    @agent
    def email_finder_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['email_finder_agent'],
            tools=[SerperDevTool()],
            output_pydantic=LeadList,
        )
    
    @agent
    def email_validator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['email_validator_agent'],
            tools=[validate_email],
            output_pydantic=ValidatedLeads,
        )

    @agent
    def data_analytics_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['data_analytics_agent'],
            tools=[save_to_google_sheets],
        )

    @task
    def scrape_leads(self) -> Task:
        return Task(
            config=self.tasks_config['scrape_leads'],
        )

    @task
    def find_lead_emails(self) -> Task:
        return Task(
            config=self.tasks_config['find_lead_emails'],
        )
    
    @task
    def validate_lead_emails(self) -> Task:
        return Task(
            config=self.tasks_config['validate_lead_emails']
        )

    @task
    def save_data(self) -> Task:
        return Task(
            config=self.tasks_config['save_data'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Lead Generation crew"""
        crew_instance = Crew(
            agents=self.agents,  # Automatically collected by the @agent decorator
            tasks=self.tasks,    # Automatically collected by the @task decorator
            process=Process.sequential,
            verbose=True,
            long_term_memory=self.long_term_memory,
            short_term_memory=self.short_term_memory,
            entity_memory=self.entity_memory,
            embedder={
               "provider": "openai",
               "config": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": "text-embedding-3-small"
               }
            },
        )
        
        return crew_instance

# Get metrics app instance
metrics_app = get_metrics_app()