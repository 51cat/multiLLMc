"""
Core base class for seminar-based cell type annotation.
"""

from typing import Optional, List, Dict, Any, Tuple

from mllmcelltype._provider import URL_DICT
from mllmcelltype.utils import add_log, get_token_counts


class BaseSeminar:
    """Base class for multi-LLM cell type annotation."""
    
    def __init__(self) -> None:
        self.support_provider = list(URL_DICT.keys())
        self.api: Optional[str] = None
        self.provider: Optional[str] = None
        self.url: Optional[str] = None
        self.token: Dict = {}
    
    @add_log
    def set_provider(self, provider: str) -> None:
        """Set the API provider."""
        if provider not in self.support_provider:
            raise KeyError(f"Provider '{provider}' not supported. Available: {self.support_provider}")
        self.provider = provider
        self.url = URL_DICT[provider]
        
        if hasattr(self.set_provider, 'logger'):
            self.set_provider.logger.info(f"provider: {self.provider}")
            self.set_provider.logger.info(f"url: {self.url}")
    
    @add_log
    def set_api(self, api: str) -> None:
        """Set the API key."""
        self.api = api
    
    @staticmethod
    def get_best_model_for_check(model_list: List[str]) -> str:
        """Get the best model for checking."""
        return model_list[0]
    
    @staticmethod
    def get_best_model_for_review(model_list: List[str]) -> str:
        """Get the best model for review."""
        return model_list[0]

    @staticmethod
    def clean_string(s: str) -> str:
        """Clean special characters from string."""
        return s.strip(' []\t\n\r')

    def get_token_counts(self, response: Any) -> Tuple[int, int, int]:
        """Extract token counts from response."""
        return get_token_counts(response)
    
    def parse_pydantic_response(self, response: Dict) -> Tuple[Dict, Any]:
        """Parse structured output response from Pydantic model."""
        raw = response.get('raw')
        parsed = response.get('parsed')
        error = response.get('parsing_error')
        
        if parsed is not None:
            parse = parsed.model_dump()
        else:
            parse = {}
        
        return parse, error
