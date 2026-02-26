"""
Harmonizer module for reaching consensus among multiple LLM annotations.
"""

from typing import Dict, List

from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

from mllmcelltype.seminar import Seminar
from mllmcelltype._promopt import make_prompt
from mllmcelltype._core import BaseSeminar
from mllmcelltype.utils import add_log, get_best_model_for_check


class ConsensusResult(BaseModel):
    """Result of single-cell annotation consensus analysis."""
    consensus_cell_type: str = Field(..., description="The finalized, unified major cell type name")
    is_consensus_reached: bool = Field(..., description="True if majority agree")
    consensus_proportion: float = Field(..., description="Ratio of models agreeing (0.0 to 1.0)")
    entropy_value: float = Field(..., description="Entropy value measuring diversity of opinions")
    reasoning: str = Field(..., description="Detailed biological justification for the consensus.")


class Harmonizer(BaseSeminar):
    """Harmonizer for reaching consensus among multiple LLM annotations."""
    
    def __init__(self, seminar_obj: Seminar) -> None:
        super().__init__()
        self.seminar = seminar_obj
        self.seminar_ai_message: Dict = {}
        self.seminar_llm_results: Dict = {}
        self.seminar_cluster_results: Dict = {}
        self.seminar_species: str = ""
        self.seminar_tissue: str = ""
        self.seminar_model_list: List[str] = []
        self.check_model: str = ""
        self.results_dict: Dict = {}
    
    @add_log
    def get_seminar_results(self) -> None:
        """Get results from the seminar object."""
        self.seminar_ai_message = self.seminar.get_ai_message()
        self.seminar_llm_results = self.seminar.get_llm_results()
        
        self.seminar_cluster_results = self.seminar.final_review_results
        self.seminar_species = self.seminar.species
        self.seminar_tissue = self.seminar.tissue
        self.seminar_model_list = self.seminar.model_list

        self.check_model = get_best_model_for_check(self.seminar_model_list)
        if hasattr(self.get_seminar_results, 'logger'):
            self.get_seminar_results.logger.info(f"check model: {self.check_model}")

    def make_consensus_promopt(self, task_name: str, annotations_input: Dict, cluster_id: str) -> str:
        """Create consensus analysis prompt."""
        return make_prompt(
            task_name,
            cluster_id=cluster_id,
            species=self.seminar_species,
            tissue=self.seminar_tissue,
            annotations=str(annotations_input)
        )

    @add_log
    def check(self) -> None:
        """Perform consensus analysis for all clusters."""
        self.results_dict = {}
        
        for cluster in self.seminar_cluster_results.keys():
            cluster_id = cluster
            task_name = 'consensus_analysis'
            annotations_input = self.seminar_cluster_results[cluster_id]

            promopt = self.make_consensus_promopt(task_name, annotations_input, cluster_id)
            
            if hasattr(self.check, 'logger'):
                self.check.logger.info(f"Check: {cluster_id}")
            
            model = init_chat_model(
                model=get_best_model_for_check(self.seminar_model_list),
                model_provider="openai", 
                temperature=0.3,
                base_url=self.url,
                api_key=self.api
            )
        
            structured_llm = model.with_structured_output(ConsensusResult, include_raw=True)
            
            response = structured_llm.invoke(promopt)
            response_dict, err = self.parse_pydantic_response(response)
            self.results_dict.update({cluster_id: response_dict})

    def get_check_result(self) -> Dict:
        """Get consensus check results."""
        return self.results_dict
