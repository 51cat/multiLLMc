"""
Utility functions for logging and response parsing.
"""

import logging
from functools import wraps
import time
from datetime import timedelta
import sys
from typing import Any, Callable, Tuple, Optional, Dict

LoggerType = logging.Logger


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logFormatter = logging.Formatter(
        '[%(levelname)s][%(asctime)s] %(name)s %(message)s'
    )
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        consoleHandler = logging.StreamHandler(sys.stderr)
        consoleHandler.setFormatter(logFormatter)
        logger.addHandler(consoleHandler)
    
    return logger


def add_log(func: Callable) -> Callable:
    """Decorator to add logging to a function."""
    logger = get_logger(f'{func.__module__}.{func.__name__}')
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info('start...')
        start = time.time()
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(f'Error: {e}')
            raise
        
        end = time.time()
        used = timedelta(seconds=end - start)
        logger.info('done. time used: %s', used)
        
        return result
    
    wrapper.logger = logger  # type: ignore
    return wrapper


def get_token_counts(response: Any) -> Tuple[int, int, int]:
    """
    Extract token counts from response.
    
    Returns:
        Tuple of (input_tokens, output_tokens, total_tokens)
    """
    usage = getattr(response, 'usage_metadata', {})
    
    input_tokens = usage.get('input_tokens', 0) if isinstance(usage, dict) else 0
    if not input_tokens:
        additional_kwargs = getattr(response, 'additional_kwargs', {})
        input_tokens = additional_kwargs.get('token_usage', {}).get('prompt_tokens', 0)
    
    output_tokens = usage.get('output_tokens', 0) if isinstance(usage, dict) else 0
    if not output_tokens:
        additional_kwargs = getattr(response, 'additional_kwargs', {})
        output_tokens = additional_kwargs.get('token_usage', {}).get('completion_tokens', 0)
    
    total_tokens = input_tokens + output_tokens
    
    return input_tokens, output_tokens, total_tokens


def clean_string(s: str) -> str:
    """Clean special characters from string."""
    return s.strip(' []\t\n\r')


def get_best_model_for_check(model_list: list) -> str:
    """Get the best model for consensus checking."""
    if not model_list:
        raise ValueError("Model list cannot be empty")
    return model_list[0]


def get_best_model_for_review(model_list: list) -> str:
    """Get the best model for review."""
    if not model_list:
        raise ValueError("Model list cannot be empty")
    return model_list[0]


def safe_json_parse(content: str) -> Optional[Dict]:
    """Safely parse JSON from string, handling common formatting issues."""
    import json
    
    content = content.strip()
    
    for char in ["'", '"']:
        if content.startswith(char) and content.endswith(char):
            content = content[1:-1]
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None
