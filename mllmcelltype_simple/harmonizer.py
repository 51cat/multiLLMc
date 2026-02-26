from langchain.chat_models import init_chat_model
from seminar import Seminar
from _promopt import make_prompt
from _core import BaseSeminar
from utils import  add_log,get_best_model_for_check
from pydantic import BaseModel, Field

class ConsensusResult(BaseModel):

    """Result of single-cell annotation consensus analysis."""
    consensus_cell_type: str = Field(..., description="The finalized, unified major cell type name")
    is_consensus_reached: bool = Field(..., description="1 if majority agree, 0 otherwise")
    consensus_proportion: float = Field(..., description="Ratio of models agreeing (0.0 to 1.0)")
    entropy_value: float = Field(..., description="Entropy value measuring diversity of opinions")
    reasoning: str = Field(..., description="Detailed biological justification for the consensus. \
                           Explain why certain models were prioritized, how synonyms were merged, \
                           and evaluate the confidence based on canonical markers cited.")

class Harmonizer(BaseSeminar):
    def __init__(
            self,
            seminar_obj: Seminar
            ) -> None:
        
        super().__init__()
        self.seminar = seminar_obj
    
    @add_log
    def get_seminar_results(self):
        self.seminar_ai_message = self.seminar.get_ai_message()
        self.seminar_llm_results = self.seminar.get_llm_results()
        
        self.seminar_cluster_results = self.seminar.final_review_results
        self.seminar_species = self.seminar.species
        self.seminar_tissue = self.seminar.tissue
        self.seminar_tissue = self.seminar.model_list

        self.check_model = get_best_model_for_check(self.seminar.model_list)
        self.get_seminar_results.logger.info(f"check model: {self.check_model}")
    

    def make_consensus_promopt(self, task_name, annotations_input, cluster_id):
        prompt_text = make_prompt(
            task_name,
            cluster_id=cluster_id,
            species= self.seminar_species,
            tissue=self.seminar_tissue,
            annotations=str(annotations_input)
        )
        return prompt_text

    @add_log
    def check(self):
        self.results_dict = {} 
        for cluster in self.seminar_cluster_results.keys(): 
            cluster_id = cluster
            task_name = 'consensus_analysis'
            annotations_input = self.seminar_cluster_results[cluster_id]

            promopt = self.make_consensus_promopt(task_name,annotations_input,cluster_id)
            self.check.logger.info(f"Check: {cluster_id}")
            model = init_chat_model(
                    model=get_best_model_for_check(self.seminar.model_list),
                    model_provider="openai", 
                    temperature=0.3,
                    base_url = self.url,
                    api_key = self.api
                )
            
            structured_llm = model.with_structured_output(ConsensusResult,include_raw=True)
            
            response = structured_llm.invoke(promopt)
            response_dict, err = self.parse_pydantic_response(response)
            self.results_dict.update({cluster_id:response_dict})

    def get_check_result(self):
        return self.results_dict