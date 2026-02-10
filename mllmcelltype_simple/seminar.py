from langchain.chat_models import init_chat_model
from collections import defaultdict

from _promopt import make_prompt
from _core import BaseSeminar
from utils import get_token_counts, clean_string, add_log
import re    
import json

class Seminar(BaseSeminar):
    def __init__(
            self,
            marker_dict,
            species = 'human',
            tissue = 'PBMC',
            tissue_desc = ''
            ) -> None:
        
        super().__init__()

        self.marker_dict = marker_dict
        self.temperature = 0
        self.species = species
        self.tissue = tissue
        self.tissue_desc = tissue_desc
        self.final_review_results = {}
        self.model_list = []

        if self.tissue_desc == '':
            self.tissue_desc = False

    @add_log
    def set_model_list(self, model_list):
        self.model_list = model_list
        self.set_model_list.logger.info(f"models: {self.model_list}")

    def _parse_marker_dict(self):
        marker_list = []
        for k, v in self.marker_dict.items():
            gene_str = ','.join(v)
            marker_list.append(
                f"{k}:{gene_str}"
            )
        self.marker_str = '\n'.join(marker_list)

    
    @add_log
    def make_init_ann_promopt2(self, task_name, spec, tissue, markers, tissue_desc):
        #self._parse_marker_dict()
        self.promopt = make_prompt(
            task_name,
            spec=spec, 
            tissue=tissue, 
            markers=markers,
            tissue_desc = tissue_desc
        )
    
    def make_init_ann_promopt(self, task_name):
        self._parse_marker_dict()
        self.promopt = make_prompt(
            task_name,
            species=self.species, 
            tissue=self.tissue, 
            cluster_list= list(self.marker_dict.keys())[0:2] if len(self.marker_dict.keys()) >=2 else  list(self.marker_dict.keys())[0],
            markers=self.marker_str,
            desc = self.tissue_desc
        )

    def parse_response(self, response):
        answer_dict = defaultdict(lambda: defaultdict(dict))
        answer = response.content

        answer_each_cluster = [c for c in re.split(r'\n+', answer) if c.strip()]
        for cluster_res in answer_each_cluster:
            cluster, celltype_res, detail = cluster_res.split("::")
            answer_dict['celltype'][cluster] = celltype_res
            answer_dict['detail'][cluster] = clean_string(detail)
        answer_dict['token'] = get_token_counts(response)
        return answer_dict


    @add_log
    def start(self):
        self.response_final_dict = {}
        self.ai_message_dict = {}

        for model_use in self.model_list:
            self.start.logger.info(f'start: {model_use}')
            try:
                model = init_chat_model(
                    model=model_use,
                    model_provider="openai", 
                    temperature=self.temperature,
                    base_url = self.url,
                    api_key = self.api
                )
                model_response = model.invoke(self.promopt)
                #print(model_response)
                print(type(model_response.content))
                response = json.loads(str(model_response.content.strip("'").strip("'").strip('"').strip('"')))
                
                
                #self.ai_message_dict.update({model_use:model_response})

                #response = self.parse_response(model_response)
                
                self.response_final_dict.update({model_use:response})
            except:
                print(f'skip {model_use}')
                continue

            self.start.logger.info(f'finish: {model_use}')

    
    @add_log
    def get_cluster_results(self):
        cluster_results = {}
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

    def get_llm_results(self):
        return self.response_final_dict
    
    def get_ai_message(self):
        return self.ai_message_dict



def main():
    api = "sk-VW019xQdJlI0EJKpESIj8UcUYWTMyBop78hsJQ2W5P8ppe3D"
    models = ['grok-3', 'deepseek-v3.2', 'qwen-plus']
    
    all_marker_genes = {
        "cluster_0": ["CD3D", "CD3E", "CD3G", "IL7R", "TCF7","HBB", "HBA1", "HBA2", "ALAS2"],        # T cells
        "cluster_1": ["CD79A", "CD79B", "MS4A1", "IGHM", "IGKC"],     # B cells
        "cluster_2": ["CD14", "LYZ", "S100A8", "S100A9", "FCN1"],     # Monocytes  
        "cluster_3": ["FCGR3A", "NCR1", "KLRD1", "GNLY", "PRF1"],     # NK cells
        "cluster_4": ["TAS2R38", "ACTN3", "ABCC11", "DEC2",'FOXP2'],             # Epithelial cells
        #"cluster_5": ["COL1A1", "COL3A1", "FN1", "VIM"],             # Fibroblasts
        #"cluster_6": ["PECAM1", "VWF", "ENG", "CDH5"],               # Endothelial cells
        #"cluster_7": ["PPBP", "PF4", "TUBB1", "GP9", "ITGA2B"],      # Platelets
        #"cluster_8": ["HBB", "HBA1", "HBA2", "ALAS2"],               # Erythrocytes
        #"cluster_9": ["TPSAB1", "TPSB2", "CPA3", "MS4A2"]           # Mast cells
    }

    celltype_seminar = Seminar(
        all_marker_genes
    )

    celltype_seminar.set_api(api)
    celltype_seminar.set_model_list(models)
    celltype_seminar.set_provider('n1n')
    celltype_seminar.make_init_ann_promopt('major_celltype')
    celltype_seminar.start()

    celltype_seminar.get_cluster_results()
    ai_res = celltype_seminar.get_ai_message()
    print(ai_res)

if __name__ == '__main__':
    main()

