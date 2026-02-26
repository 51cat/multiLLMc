"""
Tests for MultiLLMc
"""

import pytest
from mllmcelltype._provider import URL_DICT
from mllmcelltype._core import BaseSeminar
from mllmcelltype.utils import clean_string, get_best_model_for_check


class TestProvider:
    def test_url_dict_exists(self):
        assert 'n1n' in URL_DICT
        assert 'openrouter' in URL_DICT
    
    def test_url_dict_values(self):
        assert URL_DICT['n1n'] == 'https://api.n1n.ai/v1/'
        assert URL_DICT['openrouter'] == 'https://openrouter.ai/api/v1/'


class TestBaseSeminar:
    def test_init(self):
        seminar = BaseSeminar()
        assert seminar.api is None
        assert seminar.provider is None
        assert seminar.url is None
        assert 'n1n' in seminar.support_provider
    
    def test_set_api(self):
        seminar = BaseSeminar()
        seminar.set_api('test-api-key')
        assert seminar.api == 'test-api-key'
    
    def test_set_provider(self):
        seminar = BaseSeminar()
        seminar.set_provider('n1n')
        assert seminar.provider == 'n1n'
        assert seminar.url == 'https://api.n1n.ai/v1/'
    
    def test_set_invalid_provider(self):
        seminar = BaseSeminar()
        with pytest.raises(KeyError):
            seminar.set_provider('invalid_provider')
    
    def test_clean_string(self):
        assert BaseSeminar.clean_string('  test  ') == 'test'
        assert BaseSeminar.clean_string('[test]') == 'test'
        assert BaseSeminar.clean_string('\ntest\n') == 'test'


class TestUtils:
    def test_clean_string(self):
        assert clean_string('  hello  ') == 'hello'
        assert clean_string('[hello]') == 'hello'
        assert clean_string('\thello\t') == 'hello'
    
    def test_get_best_model_for_check(self):
        models = ['model-a', 'model-b', 'model-c']
        assert get_best_model_for_check(models) == 'model-a'
    
    def test_get_best_model_for_check_empty(self):
        with pytest.raises(ValueError):
            get_best_model_for_check([])
