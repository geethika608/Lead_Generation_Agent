from fastapi import FastAPI
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge, REGISTRY
import time

# Track if metrics have been registered to prevent duplicates
_metrics_registered = False
_app_instance = None

def _register_metrics():
    """Register metrics only once to prevent duplicates"""
    global _metrics_registered
    if _metrics_registered:
        return
    
    # --- Agent, Task, and Workflow Metrics ---
    global agent_execution_count, agent_execution_duration, agent_error_count
    global task_execution_count, task_execution_duration, task_error_count
    global workflow_run_count, workflow_success_count, workflow_failure_count, workflow_duration
    
    # --- Evaluation Results Analytics ---
    global evaluation_score, evaluation_count, evaluation_pass_count, evaluation_fail_count
    
    # --- Lead Analytics ---
    global leads_found
    
    agent_execution_count = Counter(
        'agent_execution_count',
        'Number of times each agent is executed',
        ['agent']
    )
    agent_execution_duration = Histogram(
        'agent_execution_duration_seconds',
        'Execution duration of each agent in seconds',
        ['agent']
    )
    agent_error_count = Counter(
        'agent_error_count',
        'Number of errors encountered by each agent',
        ['agent']
    )

    task_execution_count = Counter(
        'task_execution_count',
        'Number of times each task is executed',
        ['task']
    )
    task_execution_duration = Histogram(
        'task_execution_duration_seconds',
        'Execution duration of each task in seconds',
        ['task']
    )
    task_error_count = Counter(
        'task_error_count',
        'Number of errors encountered by each task',
        ['task']
    )

    workflow_run_count = Counter(
        'workflow_run_count',
        'Number of workflow runs'
    )
    workflow_success_count = Counter(
        'workflow_success_count',
        'Number of successful workflow completions'
    )
    workflow_failure_count = Counter(
        'workflow_failure_count',
        'Number of failed workflow runs'
    )
    workflow_duration = Histogram(
        'workflow_duration_seconds',
        'Workflow execution duration in seconds'
    )

    # --- Evaluation Results Analytics ---
    evaluation_score = Histogram(
        'evaluation_score',
        'Distribution of evaluation scores'
    )
    evaluation_count = Counter(
        'evaluation_count',
        'Number of workflow evaluations'
    )
    evaluation_pass_count = Counter(
        'evaluation_pass_count',
        'Number of workflow evaluations that passed'
    )
    evaluation_fail_count = Counter(
        'evaluation_fail_count',
        'Number of workflow evaluations that failed'
    )

    # --- Lead Analytics ---
    leads_found = Counter(
        'leads_found_total',
        'Total number of leads found'
    )

    _metrics_registered = True

def get_metrics_app() -> FastAPI:
    """Get FastAPI app with Prometheus metrics endpoint"""
    global _app_instance
    if _app_instance is None:
        _register_metrics()
        app = FastAPI(title="Lead Generation Agent Metrics")
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
        _app_instance = app
    return _app_instance

def record_workflow_start():
    """Record workflow start"""
    _register_metrics()
    workflow_run_count.inc()

def record_workflow_completion(duration: float, success: bool):
    """Record workflow completion"""
    _register_metrics()
    workflow_duration.observe(duration)
    if success:
        workflow_success_count.inc()
    else:
        workflow_failure_count.inc()

def record_evaluation_result(score: float, passed: bool):
    """Record evaluation result"""
    _register_metrics()
    evaluation_score.observe(score)
    evaluation_count.inc()
    if passed:
        evaluation_pass_count.inc()
    else:
        evaluation_fail_count.inc()

def record_lead_analytics(found: int):
    """Record lead analytics"""
    _register_metrics()
    leads_found.inc(found)

def record_agent_execution(agent: str, duration: float, error: bool = False):
    """Record agent execution"""
    _register_metrics()
    agent_execution_count.labels(agent=agent).inc()
    agent_execution_duration.labels(agent=agent).observe(duration)
    if error:
        agent_error_count.labels(agent=agent).inc()

def record_task_execution(task: str, duration: float, error: bool = False):
    """Record task execution"""
    _register_metrics()
    task_execution_count.labels(task=task).inc()
    task_execution_duration.labels(task=task).observe(duration)
    if error:
        task_error_count.labels(task=task).inc() 