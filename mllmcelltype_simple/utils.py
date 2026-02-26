import logging
from functools import wraps
import time
from datetime import timedelta
import sys

def add_log(func):
    logFormatter = logging.Formatter(
        '[%(levelname)s][%(asctime)s] %(name)s %(message)s'
    )

    # 创建一个日志器
    logger = logging.getLogger(
        f'{func.__module__}.{func.__name__}'
    )
    
    # 设置日志级别
    logger.setLevel(logging.INFO)

    # 创建一个控制台处理器
    consoleHandler = logging.StreamHandler(sys.stderr)
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info('start...')
        start = time.time()

        result = func(*args, **kwargs)
    
        end = time.time()
        used = timedelta(seconds=end - start)
        logger.info('done. time used: %s', used)
        
        return result

    wrapper.logger = logger
    return wrapper

def get_token_counts(response):
    """
    提取 Token 数量：返回 (input_tokens, output_tokens, total_tokens)
    """
    # 兼容 usage_metadata 和 additional_kwargs 两种情况
    usage = getattr(response, 'usage_metadata', {})
    
    input_tokens = usage.get('input_tokens') or \
                   response.additional_kwargs.get('token_usage', {}).get('prompt_tokens', 0)
                   
    output_tokens = usage.get('output_tokens') or \
                    response.additional_kwargs.get('token_usage', {}).get('completion_tokens', 0)
    
    total_tokens = input_tokens + output_tokens
    
    return input_tokens, output_tokens, total_tokens


def clean_string(s):
    # strip() 括号里写上你想要剔除的所有特殊字符
    # 这里的 ' []\t\n' 表示空格、左右方括号、制表符和换行符
    return s.strip(' []\t\n\r')


def get_best_model_for_check(model_list):
    return model_list[0]