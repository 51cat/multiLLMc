"""
Example: Basic cell type annotation with MultiLLMc
"""

from mllmcelltype import Seminar

# Define marker genes for each cluster
all_marker_genes = {
    "cluster_0": ["CD3D", "CD3E", "CD3G", "IL7R", "TCF7"],
    "cluster_1": ["CD79A", "CD79B", "MS4A1", "IGHM", "IGKC"],
    "cluster_2": ["CD14", "LYZ", "S100A8", "S100A9", "FCN1"],
    "cluster_3": ["FCGR3A", "NCR1", "KLRD1", "GNLY", "PRF1"],
    "cluster_4": ["COL1A1", "COL3A1", "FN1", "VIM"],
}

# Initialize seminar
celltype_seminar = Seminar(
    marker_dict=all_marker_genes,
    species='human',
    tissue='PBMC'
)

# Configure API and models
celltype_seminar.set_api("your-api-key-here")
celltype_seminar.set_model_list(['gpt-4o', 'claude-3-sonnet', 'gemini-pro'])
celltype_seminar.set_provider('openrouter')

# Make prompt and run
celltype_seminar.make_init_ann_promopt('major_celltype')
celltype_seminar.start()

# Get results
results = celltype_seminar.get_cluster_results()
print("Annotation Results:")
for cluster, annotations in results.items():
    print(f"\n{cluster}:")
    for model, annotation in annotations.items():
        print(f"  {model}: {annotation['celltype']}")
