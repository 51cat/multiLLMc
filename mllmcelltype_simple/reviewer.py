from langchain.chat_models import init_chat_model
from seminar import Seminar
from _core import BaseSeminar
from _promopt import make_prompt
from utils import add_log


from pydantic import BaseModel, Field

MAX_REVIEW_COUNTS = 3


class AuditResult(BaseModel):
    """Result of single-cell annotation quality audit by a senior transcriptomics expert."""
    is_gene_faithful: bool = Field(
        ..., 
        description="True if the AI strictly used the provided marker genes without hallucinating or inventing non-existent markers for the cluster."
    )
    is_biologically_valid: bool = Field(
        ..., 
        description="True if the cell type inference aligns with established biological facts and tissue-specific contexts in scRNA-seq."
    )
    reliability_score: float = Field(
        ..., 
        ge=0, le=100,
        description="A confidence score from 0 to 100, reflecting the overall trustworthiness based on marker evidence and biological logic."
    )
    audit_reasoning: str = Field(
        ..., 
        description="Detailed biological and technical justification for the audit. \
                     Explain if any marker genes were hallucinated, evaluate the tissue-specific \
                     plausibility, and justify the reliability score based on single-cell expert knowledge."
    )

class ReannotationResult(BaseModel):
    """The final corrected annotation result after expert audit and self-correction."""
    celltype: str  = Field(
        ..., 
        description="The finalized, corrected broad major cell type name after addressing expert feedback."
    )
    detail: str = Field(
        ..., 
        description="Comprehensive reasoning for the corrected cell type, emphasizing how the provided markers support this lineage while avoiding previous errors."
    )


class Reviewer(BaseSeminar):
    def __init__(
            self,
            seminar_obj: Seminar
            ) -> None:
        
        super().__init__()

        self.seminar = seminar_obj
        self.score_th = 60
    
    def set_score_th(self, score):
        self.score_th = score

    @add_log
    def get_seminar_results(self):
        self.seminar_ai_message = self.seminar.get_ai_message()
        self.seminar_llm_results = self.seminar.get_llm_results()
        self.seminar_cluster_results = self.seminar.get_cluster_results()

        self.seminar_species = self.seminar.species
        self.seminar_tissue = self.seminar.tissue
        self.seminar_model_list = self.seminar.model_list
        self.seminar_marker_dict = self.seminar.marker_dict

        self.review_model = self.get_best_model_for_review(self.seminar.model_list)
        self.get_seminar_results.logger.info(f"review model: {self.review_model}")
    
    def make_audit_prompt(self, task_name, cluster_id, genes, model_name, annotation_to_audit):
        prompt_text = make_prompt(
            task_name,
            species=self.seminar_species,
            tissue=self.seminar_tissue,
            cluster_id=cluster_id,
            model_name=model_name,
            genes=genes,
            anno=annotation_to_audit
        )
        return prompt_text
    
    def make_reannotate_promopt(self, task_name, ann_err, markers, review_results):
        prompt_text = make_prompt(
            task_name,
            species=self.seminar_species,
            tissue=self.seminar_tissue,
            ann_err=ann_err,
            is_gene_faithful=review_results['is_gene_faithful'],
            is_biologically_valid=review_results['is_biologically_valid'],
            reliability_score=review_results['reliability_score'],
            audit_reasoning = review_results['audit_reasoning'],
            markers = ','.join(markers)
        )
        return prompt_text

    def review_checker(self, review_result):
        f1 = review_result['is_gene_faithful']
        f2 = review_result['is_biologically_valid']
        f3 = review_result['reliability_score'] >= self.score_th

        return all([f1, f2, f3])

    @add_log
    def reanalysis_error_result(self, ann_err, marker_gene, review_results, model_use, cluster_id):
        promopt = self.make_reannotate_promopt(
                    "re_major_celltype",
                     ann_err, marker_gene, review_results
                )
        print(promopt)
        model = init_chat_model(
                    model=model_use,
                    model_provider="openai", 
                    temperature=0.7,
                    base_url = self.url,
                    api_key = self.api
                )
        
        structured_llm = model.with_structured_output(ReannotationResult,include_raw=True)
                
        response = structured_llm.invoke(promopt)
        response_dict, err = self.parse_pydantic_response(response)
        review_dict = self.review({cluster_id:{model_use:response_dict}}, only_get_res = True)
        return response_dict, review_dict


    @add_log
    def review(self, cluster_results_dict = None, only_get_res = False):
        
        if cluster_results_dict in [None, 'None']:
            cluster_results_dict = self.seminar_cluster_results

        for cluster_id in cluster_results_dict.keys():
            genes = self.seminar_marker_dict[cluster_id]
            
            for model_use in cluster_results_dict[cluster_id].keys():

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
                    base_url = self.url,
                    api_key = self.api
                )
            
                structured_llm = model.with_structured_output(AuditResult,include_raw=True)
                
                response = structured_llm.invoke(promopt)
                print(response)
                revirew_response_dict, err = self.parse_pydantic_response(response)

                if only_get_res:
                    return revirew_response_dict

                review_flag = self.review_checker(revirew_response_dict)

                if review_flag:
                    cluster_results_dict[cluster_id][model_use]['review'] = revirew_response_dict
                else:
                    
                    for inx in range(MAX_REVIEW_COUNTS):
                        self.review.logger.info(f"start: {cluster_id} - {model_use} - reannoate- times: {inx + 1}")
                        corr_res, corr_review_res = self.reanalysis_error_result(
                            cluster_results_dict[cluster_id][model_use], 
                            genes, 
                            revirew_response_dict, 
                            model_use,
                            cluster_id = cluster_id)
                        
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
                
                self.review.logger.info(f"Review: {cluster_id} - {model_use} - done")
        
        self.review_final_results =cluster_results_dict       

    def add_review_results_to_seminar(self):
        self.seminar.final_review_results = self.review_final_results
        return self.seminar