"""
DeepEval metrics configuration for evaluation
"""

from typing import List, Optional

# DeepEval imports
try:
    from deepeval.metrics import AnswerRelevancy, Faithfulness, ContextRelevancy, ContextRecall, AnswerCorrectness
    DEEPEVAL_AVAILABLE = True
except ImportError:
    DEEPEVAL_AVAILABLE = False

class MetricsConfig:
    """Configuration for DeepEval metrics"""
    
    # Default thresholds for each metric
    DEFAULT_THRESHOLDS = {
        'AnswerRelevancy': 0.7,
        'Faithfulness': 0.7,
        'ContextRelevancy': 0.7,
        'ContextRecall': 0.7,
        'AnswerCorrectness': 0.7
    }
    
    # Metric weights for overall score calculation
    METRIC_WEIGHTS = {
        'AnswerRelevancy': 0.3,
        'Faithfulness': 0.2,
        'ContextRelevancy': 0.2,
        'ContextRecall': 0.15,
        'AnswerCorrectness': 0.15
    }
    
    @classmethod
    def get_metrics(cls, custom_thresholds: Optional[dict] = None) -> List:
        """Get configured DeepEval metrics"""
        if not DEEPEVAL_AVAILABLE:
            raise ImportError("DeepEval is not available. Install with: pip install deepeval")
        
        thresholds = {**cls.DEFAULT_THRESHOLDS, **(custom_thresholds or {})}
        
        return [
            AnswerRelevancy(threshold=thresholds['AnswerRelevancy']),
            Faithfulness(threshold=thresholds['Faithfulness']),
            ContextRelevancy(threshold=thresholds['ContextRelevancy']),
            ContextRecall(threshold=thresholds['ContextRecall']),
            AnswerCorrectness(threshold=thresholds['AnswerCorrectness'])
        ]
    
    @classmethod
    def get_weights(cls) -> dict:
        """Get metric weights for score calculation"""
        return cls.METRIC_WEIGHTS.copy()
    
    @classmethod
    def get_thresholds(cls) -> dict:
        """Get default thresholds"""
        return cls.DEFAULT_THRESHOLDS.copy()
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if DeepEval is available"""
        return DEEPEVAL_AVAILABLE 