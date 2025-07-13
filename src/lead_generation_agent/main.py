import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from .monitoring.prometheus_metrics import get_metrics_app
import yaml
from .ui.gradio_interface import create_interface

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
def load_config():
    """Load configuration from environment variables and YAML file"""
    try:
        # Load non-sensitive config from YAML
        config_path = Path(__file__).parent / 'config' / 'default_config.yaml'
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning("Config file not found, using default config")
        yaml_config = {}
    
    # Load sensitive config from environment variables
    env_config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'deepeval_api_key': os.getenv('DEEPEVAL_API_KEY'),
        'serper_api_key': os.getenv('SERPER_API_KEY'),
        'google_credentials_file': os.getenv('GOOGLE_CREDENTIALS_FILE'),
        'crewai_verbose': os.getenv('CREWAI_VERBOSE', 'true').lower() == 'true',
        'crewai_max_rpm': int(os.getenv('CREWAI_MAX_RPM', 5)),
    }
    
    # Merge configurations (env takes precedence)
    config = {**yaml_config, **env_config}
    
    # Validate required configuration
    if not config.get('openai_api_key'):
        logger.error("OPENAI_API_KEY is required but not set")
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    logger.info("Configuration loaded successfully")
    return config

def run():
    """Main entry point for the lead generation agent"""
    try:
        # Load configuration
        config = load_config()
        
        # Create and launch the interface
        interface = create_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start lead generation agent: {e}")
        raise

def train():
    """Train the lead generation agent (placeholder)"""
    logger.info("Training functionality not implemented yet")
    print("Training functionality not implemented yet")

def replay():
    """Replay previous runs (placeholder)"""
    logger.info("Replay functionality not implemented yet")
    print("Replay functionality not implemented yet")

def test():
    """Run tests (placeholder)"""
    logger.info("Test functionality not implemented yet")
    print("Test functionality not implemented yet")

def main():
    """Main entry point for the lead generation agent"""
    run()

if __name__ == "__main__":
    main()

# Get the metrics app (already has metrics mounted)
metrics_app = get_metrics_app() 