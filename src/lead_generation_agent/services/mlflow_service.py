"""
Simple MLflow tracking service for the Lead Generation Agent
"""

import os
import mlflow
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MLflowService:
    """Simple service for MLflow experiment tracking"""
    
    def __init__(self):
        """Initialize MLflow service"""
        self.tracking_uri = os.getenv('MLFLOW_TRACKING_URI', 'file:./mlflow')
        self.experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', 'lead-generation-agent')
        
        print(f"🔧 Initializing MLflow with tracking URI: {self.tracking_uri}")
        print(f"🔧 Experiment name: {self.experiment_name}")
        logger.info(f"Initializing MLflow with tracking URI: {self.tracking_uri}")
        logger.info(f"Experiment name: {self.experiment_name}")
        
        # Set up MLflow
        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            self._setup_experiment()
            mlflow.crewai.autolog()
        except Exception as e:
            print(f"❌ Failed to initialize MLflow: {e}")
            logger.error(f"Failed to initialize MLflow: {e}")
            # Fallback to local file tracking
            print("🔄 Falling back to local file tracking")
            logger.info("Falling back to local file tracking")
            mlflow.set_tracking_uri("file:./mlflow")
            self._setup_experiment()
        
    def _setup_experiment(self):
        """Set up the MLflow experiment"""
        try:
            # Create experiment if it doesn't exist
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                print(f"📁 Creating new experiment: {self.experiment_name}")
                logger.info(f"Creating new experiment: {self.experiment_name}")
                mlflow.create_experiment(name=self.experiment_name)
            else:
                print(f"📁 Using existing experiment: {self.experiment_name}")
                logger.info(f"Using existing experiment: {self.experiment_name}")
            
            mlflow.set_experiment(self.experiment_name)
            print(f"✅ MLflow experiment '{self.experiment_name}' is ready")
            logger.info(f"MLflow experiment '{self.experiment_name}' is ready")
            
        except Exception as e:
            print(f"❌ Failed to set up MLflow experiment: {e}")
            logger.error(f"Failed to set up MLflow experiment: {e}")
            # Fallback to local tracking
            print("🔄 Falling back to local file tracking")
            logger.info("Falling back to local file tracking")
            mlflow.set_tracking_uri("file:./mlflow")
            mlflow.set_experiment(self.experiment_name)
    
    def start_run(self, run_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> str:
        """Start a new MLflow run"""
        try:
            if run_name is None:
                run_name = f"lead-generation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            print(f"🚀 Starting MLflow run: {run_name}")
            print(f"🏷️  Tags: {tags}")
            logger.info(f"Starting MLflow run: {run_name}")
            logger.info(f"Tags: {tags}")
            
            mlflow.start_run(run_name=run_name, tags=tags or {})
            run_id = mlflow.active_run().info.run_id
            print(f"✅ Successfully started MLflow run: {run_name}")
            print(f"🆔 Run ID: {run_id}")
            logger.info(f"Successfully started MLflow run: {run_name} (ID: {run_id})")
            return run_id
            
        except Exception as e:
            print(f"❌ Failed to start MLflow run: {e}")
            print(f"🔍 Run name: {run_name}, Tags: {tags}")
            logger.error(f"Failed to start MLflow run: {e}")
            logger.error(f"Run name: {run_name}, Tags: {tags}")
            return None
    
    def end_run(self):
        """End the current MLflow run"""
        try:
            print("🏁 Ending MLflow run")
            logger.info("Ending MLflow run")
            mlflow.end_run()
            print("✅ Successfully ended MLflow run")
            logger.info("Successfully ended MLflow run")
        except Exception as e:
            print(f"❌ Failed to end MLflow run: {e}")
            logger.error(f"Failed to end MLflow run: {e}")


# Global MLflow service instance
mlflow_service = MLflowService() 