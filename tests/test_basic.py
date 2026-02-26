"""
Tests for MultiLLMc
"""

import pytest
from typing import Dict, List

from mllmcelltype._provider import URL_DICT
from mllmcelltype._core import BaseSeminar
from mllmcelltype.utils import clean_string, get_best_model_for_check, get_best_model_for_review, safe_json_parse
from mllmcelltype._promopt import make_prompt, PROMPT_DICT


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
    
    def test_get_best_model_empty_list(self):
        with pytest.raises(ValueError):
            BaseSeminar.get_best_model_for_check([])
        
        with pytest.raises(ValueError):
            BaseSeminar.get_best_model_for_review([])


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
    
    def test_get_best_model_for_review_empty(self):
        with pytest.raises(ValueError):
            get_best_model_for_review([])
    
    def test_safe_json_parse(self):
        result = safe_json_parse('{"key": "value"}')
        assert result == {"key": "value"}
        
        result = safe_json_parse('\'{"key": "value"}\'')
        assert result == {"key": "value"}
        
        result = safe_json_parse('invalid json')
        assert result is None


class TestPrompts:
    def test_prompt_dict_keys(self):
        expected_keys = ['major_celltype', 're_major_celltype', 'consensus_analysis', 'review_analysis', 'new']
        for key in expected_keys:
            assert key in PROMPT_DICT
    
    def test_make_prompt_major_celltype(self):
        prompt = make_prompt(
            'major_celltype',
            species='human',
            tissue='PBMC',
            cluster_list=['cluster_0', 'cluster_1'],
            markers='cluster_0:CD3D,CD3E\ncluster_1:CD79A,CD79B',
            desc=False
        )
        assert 'human' in prompt
        assert 'PBMC' in prompt
        assert 'cluster_0:CD3D,CD3E' in prompt
    
    def test_make_prompt_review_analysis(self):
        prompt = make_prompt(
            'review_analysis',
            species='human',
            tissue='PBMC',
            cluster_id='cluster_0',
            model_name='gpt-4o',
            genes=['CD3D', 'CD3E'],
            anno={'celltype': 'T cells', 'detail': 'CD3D and CD3E are T cell markers'}
        )
        assert 'human' in prompt
        assert 'PBMC' in prompt
        assert 'cluster_0' in prompt
        assert 'CD3D' in prompt
    
    def test_make_prompt_invalid_template(self):
        with pytest.raises(ValueError):
            make_prompt('invalid_template')


class TestMarkerData:
    """Test with realistic marker gene data."""
    
    def test_pbmc_markers_structure(self):
        from tests.test_markers import MARKER_GENES_PBMC
        
        assert isinstance(MARKER_GENES_PBMC, dict)
        assert len(MARKER_GENES_PBMC) == 8
        
        for cluster_id, genes in MARKER_GENES_PBMC.items():
            assert cluster_id.startswith('cluster_')
            assert isinstance(genes, list)
            assert len(genes) >= 5
    
    def test_doublet_markers(self):
        from tests.test_markers import MARKER_GENES_DOUBLET_EXAMPLE
        
        doublet_genes = MARKER_GENES_DOUBLET_EXAMPLE['cluster_doublet']
        has_t_markers = any(g in doublet_genes for g in ['CD3D', 'CD3E'])
        has_b_markers = any(g in doublet_genes for g in ['CD79A', 'MS4A1'])
        
        assert has_t_markers and has_b_markers
