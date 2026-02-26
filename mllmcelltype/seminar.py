"""
Seminar module for multi-LLM cell type annotation discussion.
"""

import json
import re
from collections import defaultdict
from typing import Dict, List, Optional, Any

from langchain.chat_models import init_chat_model

from mllmcelltype._promopt import make_prompt
from mllmcelltype._core import BaseSeminar
from mllmcelltype.utils import get_token_counts, clean_string, add_log


class Seminar(BaseSeminar):
    """Multi-LLM Seminar for cell type annotation."""
    
    def __init__(
        self,
        marker_dict: Dict[str, List[str]],
        species: str = 'human',
        tissue: str = 'PBMC',
        tissue_desc: str = ''
    ) -> None:
        super().__init__()
        
        self.marker_dict = marker_dict
        self.temperature = 0
        self.species = species
        self.tissue = tissue
        self.tissue_desc = tissue_desc if tissue_desc else False
        self.final_review_results: Dict = {}
        self.model_list: List[str] = []
        self.promopt: Optional[str] = None
        self.response_final_dict: Dict = {}
        self.ai_message_dict: Dict = {}
        self.marker_str: str = ""

    @add_log
    def set_model_list(self, model_list: List[str]) -> None:
        """Set the list of models to use."""
        self.model_list = model_list
        if hasattr(self.set_model_list, 'logger'):
            self.set_model_list.logger.info(f"models: {self.model_list}")

    def _parse_marker_dict(self) -> None:
        """Parse marker dictionary into string format."""
        marker_list = []
        for k, v in self.marker_dict.items():
            gene_str = ','.join(v)
            marker_list.append(f"{k}:{gene_str}")
        self.marker_str = '\n'.join(marker_list)
    
    @add_log
    def make_init_ann_promopt2(self, task_name: str, spec: str, tissue: str, markers: str, tissue_desc: str) -> None:
        """Make initial annotation prompt with custom parameters."""
        self.promopt = make_prompt(
            task_name,
            spec=spec, 
            tissue=tissue, 
            markers=markers,
            tissue_desc=tissue_desc
        )
    
    def make_init_ann_promopt(self, task_name: str) -> None:
        """Make initial annotation prompt."""
        self._parse_marker_dict()
        cluster_keys = list(self.marker_dict.keys())
        cluster_list = cluster_keys[0:2] if len(cluster_keys) >= 2 else cluster_keys[0]
        
        self.promopt = make_prompt(
            task_name,
            species=self.species, 
            tissue=self.tissue, 
            cluster_list=cluster_list,
            markers=self.marker_str,
            desc=self.tissue_desc
        )

    def parse_response(self, response: Any) -> Dict:
        """Parse model response into structured format."""
        answer_dict: Dict = defaultdict(lambda: defaultdict(dict))
        answer = response.content

        answer_each_cluster = [c for c in re.split(r'\n+', answer) if c.strip()]
        for cluster_res in answer_each_cluster:
            parts = cluster_res.split("::")
            if len(parts) >= 3:
                cluster, celltype_res, detail = parts[0], parts[1], parts[2]
                answer_dict['celltype'][cluster] = celltype_res
                answer_dict['detail'][cluster] = clean_string(detail)
        answer_dict['token'] = get_token_counts(response)
        return dict(answer_dict)

    @add_log
    def start(self) -> None:
        """Start the annotation process with all models."""
        self.response_final_dict = {}
        self.ai_message_dict = {}

        for model_use in self.model_list:
            if hasattr(self.start, 'logger'):
                self.start.logger.info(f'start: {model_use}')
            try:
                model = init_chat_model(
                    model=model_use,
                    model_provider="openai", 
                    temperature=self.temperature,
                    base_url=self.url,
                    api_key=self.api
                )
                model_response = model.invoke(self.promopt)
                
                content = str(model_response.content)
                content = content.strip("'").strip('"')
                response = json.loads(content)
                
                self.response_final_dict.update({model_use: response})
            except Exception as e:
                print(f'skip {model_use}: {e}')
                continue

            if hasattr(self.start, 'logger'):
                self.start.logger.info(f'finish: {model_use}')
    
    @add_log
    def get_cluster_results(self) -> Dict:
        """Get results organized by cluster."""
        cluster_results: Dict = {}
        for model_name, model_data in self.response_final_dict.items():
            celltypes = model_data.get('celltype', {})
            details = model_data.get('detail', {})
            for cluster_id, celltype in celltypes.items():
                detail_str = details.get(cluster_id, "")
                if cluster_id not in cluster_results:
                    cluster_results[cluster_id] = {}
                cluster_results[cluster_id][model_name] = {
                    "celltype": celltype,
                    "detail": detail_str
                }
        return cluster_results

    def get_llm_results(self) -> Dict:
        """Get raw LLM results."""
        return self.response_final_dict
    
    def get_ai_message(self) -> Dict:
        """Get AI message objects."""
        return self.ai_message_dict
