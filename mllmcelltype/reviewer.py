"""
Reviewer module for auditing and correcting cell type annotations.
"""

from typing import Dict, List, Any, Optional

from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

from mllmcelltype.seminar import Seminar
from mllmcelltype._core import BaseSeminar
from mllmcelltype._promopt import make_prompt
from mllmcelltype.utils import add_log


MAX_REVIEW_COUNTS = 3


class AuditResult(BaseModel):
    """Result of single-cell annotation quality audit by a senior transcriptomics expert."""
    is_gene_faithful: bool = Field(
        ..., 
        description="True if the AI strictly used the provided marker genes without hallucinating."
    )
    is_biologically_valid: bool = Field(
        ..., 
        description="True if the cell type inference aligns with established biological facts."
    )
    reliability_score: float = Field(
        ..., 
        ge=0, le=100,
        description="A confidence score from 0 to 100."
    )
    audit_reasoning: str = Field(
        ..., 
        description="Detailed biological and technical justification for the audit."
    )


class ReannotationResult(BaseModel):
    """The final corrected annotation result after expert audit and self-correction."""
    celltype: str = Field(
        ..., 
        description="The finalized, corrected broad major cell type name."
    )
    detail: str = Field(
        ..., 
        description="Comprehensive reasoning for the corrected cell type."
    )


class Reviewer(BaseSeminar):
    """Reviewer for auditing and correcting annotations."""
    
    def __init__(self, seminar_obj: Seminar) -> None:
        super().__init__()
        self.seminar = seminar_obj
        self.score_th = 60
        self.seminar_ai_message: Dict = {}
        self.seminar_llm_results: Dict = {}
        self.seminar_cluster_results: Dict = {}
        self.seminar_species: str = ""
        self.seminar_tissue: str = ""
        self.seminar_model_list: List[str] = []
        self.seminar_marker_dict: Dict = {}
        self.review_model: str = ""
        self.review_final_results: Dict = {}
    
    def set_score_th(self, score: int) -> None:
        """Set the score threshold for passing review."""
        self.score_th = score

    @add_log
    def get_seminar_results(self) -> None:
        """Get results from the seminar object."""
        self.seminar_ai_message = self.seminar.get_ai_message()
        self.seminar_llm_results = self.seminar.get_llm_results()
        self.seminar_cluster_results = self.seminar.get_cluster_results()

        self.seminar_species = self.seminar.species
        self.seminar_tissue = self.seminar.tissue
        self.seminar_model_list = self.seminar.model_list
        self.seminar_marker_dict = self.seminar.marker_dict

        self.review_model = self.get_best_model_for_review(self.seminar.model_list)
        if hasattr(self.get_seminar_results, 'logger'):
            self.get_seminar_results.logger.info(f"review model: {self.review_model}")
    
    def make_audit_prompt(self, task_name: str, cluster_id: str, genes: List[str], model_name: str, annotation_to_audit: Dict) -> str:
        """Create audit prompt for a specific annotation."""
        return make_prompt(
            task_name,
            species=self.seminar_species,
            tissue=self.seminar_tissue,
            cluster_id=cluster_id,
            model_name=model_name,
            genes=genes,
            anno=annotation_to_audit
        )
    
    def make_reannotate_promopt(self, task_name: str, ann_err: Dict, markers: List[str], review_results: Dict) -> str:
        """Create re-annotation prompt based on audit results."""
        return make_prompt(
            task_name,
            species=self.seminar_species,
            tissue=self.seminar_tissue,
            ann_err=ann_err,
            is_gene_faithful=review_results['is_gene_faithful'],
            is_biologically_valid=review_results['is_biologically_valid'],
            reliability_score=review_results['reliability_score'],
            audit_reasoning=review_results['audit_reasoning'],
            markers=','.join(markers)
        )

    def review_checker(self, review_result: Dict) -> bool:
        """Check if review result passes the threshold."""
        f1 = review_result['is_gene_faithful']
        f2 = review_result['is_biologically_valid']
        f3 = review_result['reliability_score'] >= self.score_th
        return all([f1, f2, f3])

    @add_log
    def reanalysis_error_result(self, ann_err: Dict, marker_gene: List[str], review_results: Dict, model_use: str, cluster_id: str) -> tuple:
        """Re-analyze an error result."""
        promopt = self.make_reannotate_promopt(
            "re_major_celltype",
            ann_err, marker_gene, review_results
        )
        
        model = init_chat_model(
            model=model_use,
            model_provider="openai", 
            temperature=0.7,
            base_url=self.url,
            api_key=self.api
        )
        
        structured_llm = model.with_structured_output(ReannotationResult, include_raw=True)
        response = structured_llm.invoke(promopt)
        response_dict, err = self.parse_pydantic_response(response)
        review_dict = self.review({cluster_id: {model_use: response_dict}}, only_get_res=True)
        return response_dict, review_dict

    @add_log
    def review(self, cluster_results_dict: Optional[Dict] = None, only_get_res: bool = False) -> Optional[Dict]:
        """Review all annotations."""
        if cluster_results_dict is None:
            cluster_results_dict = self.seminar_cluster_results
        
        if cluster_results_dict is None:
            return None

        for cluster_id in cluster_results_dict.keys():
            genes = self.seminar_marker_dict.get(cluster_id, [])
            
            for model_use in cluster_results_dict[cluster_id].keys():
                if hasattr(self.review, 'logger'):
                    self.review.logger.info(f"start Review: {cluster_id} - {model_use}")

                annotation_to_audit = cluster_results_dict[cluster_id][model_use]

                promopt = self.make_audit_prompt(
                    "review_analysis",
                    cluster_id, genes, model_use, annotation_to_audit
                )
                
                model = init_chat_model(
                    model=self.review_model,
                    model_provider="openai", 
                    temperature=0.7,
                    base_url=self.url,
                    api_key=self.api
                )
            
                structured_llm = model.with_structured_output(AuditResult, include_raw=True)
                response = structured_llm.invoke(promopt)
                review_response_dict, err = self.parse_pydantic_response(response)

                if only_get_res:
                    return review_response_dict

                review_flag = self.review_checker(review_response_dict)

                if review_flag:
                    cluster_results_dict[cluster_id][model_use]['review'] = review_response_dict
                else:
                    corr_res: Dict = {}
                    corr_review_res: Dict = {}
                    
                    for inx in range(MAX_REVIEW_COUNTS):
                        if hasattr(self.review, 'logger'):
                            self.review.logger.info(f"start: {cluster_id} - {model_use} - reannoate- times: {inx + 1}")
                        corr_res, corr_review_res = self.reanalysis_error_result(
                            cluster_results_dict[cluster_id][model_use], 
                            genes, 
                            review_response_dict, 
                            model_use,
                            cluster_id=cluster_id
                        )
                        
                        review_flag = self.review_checker(corr_review_res)

                        if review_flag:
                            cluster_results_dict[cluster_id][model_use] = corr_res
                            cluster_results_dict[cluster_id][model_use]['review'] = corr_review_res
                            break
                    
                    if review_flag:
                        cluster_results_dict[cluster_id][model_use] = corr_res
                        cluster_results_dict[cluster_id][model_use]['review'] = corr_review_res
                    else:
                        cluster_results_dict[cluster_id][model_use]['celltype'] = 'unknown'
                        cluster_results_dict[cluster_id][model_use]['review'] = corr_review_res
                
                if hasattr(self.review, 'logger'):
                    self.review.logger.info(f"Review: {cluster_id} - {model_use} - done")
        
        self.review_final_results = cluster_results_dict
        return None

    def add_review_results_to_seminar(self) -> Seminar:
        """Add review results back to seminar object."""
        self.seminar.final_review_results = self.review_final_results
        return self.seminar
