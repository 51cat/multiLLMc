from _provider import URL_DICT
from utils import add_log

class BaseSeminar:
    def __init__(self) -> None:
        self.support_provider = list(URL_DICT.keys())
        self.api = None
        self.provider = None
        self.token = {}
    
    @add_log
    def set_provider(self, provider):
        if provider not in self.support_provider:
            raise KeyError
        self.provider = provider
        self.url = URL_DICT[provider]

        self.set_provider.logger.info(f"provider: {self.provider}")
        self.set_provider.logger.info(f"url: {self.url}")

    @add_log
    def set_api(self, api):
        self.api = api
    
    @staticmethod
    def get_best_model_for_check(model_list):
        return model_list[0]
    
    @staticmethod
    def get_best_model_for_review(model_list):
        return model_list[0]

    @staticmethod
    def clean_string(s):
        # strip() 括号里写上你想要剔除的所有特殊字符
        # 这里的 ' []\t\n' 表示空格、左右方括号、制表符和换行符
        return s.strip(' []\t\n\r')

    def get_token_counts(self, response):
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
    
    def parse_pydantic_response(self, response):
        
        raw = response['raw']
        token = self.get_token_counts(raw)
        
        parse = response['parsed'].model_dump()
        error = response['parsing_error']
        
        return parse, error