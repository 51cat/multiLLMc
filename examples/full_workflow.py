"""
Example: Full workflow with review and harmonization
"""

from mllmcelltype import Seminar, Reviewer, Harmonizer

# Define marker genes
all_marker_genes = {
    "cluster_0": ["CD3D", "CD3E", "CD3G", "IL7R", "TCF7"],
    "cluster_1": ["CD79A", "CD79B", "MS4A1", "IGHM", "IGKC"],
    "cluster_2": ["CD14", "LYZ", "S100A8", "S100A9", "FCN1"],
}

# Step 1: Initialize and run seminar
print("Step 1: Running multi-LLM annotation...")
seminar = Seminar(
    marker_dict=all_marker_genes,
    species='human',
    tissue='PBMC'
)

seminar.set_api("your-api-key-here")
seminar.set_model_list(['gpt-4o', 'claude-3-sonnet'])
seminar.set_provider('openrouter')
seminar.make_init_ann_promopt('major_celltype')
seminar.start()

# Step 2: Review annotations
print("Step 2: Reviewing annotations...")
reviewer = Reviewer(seminar)
reviewer.set_api("your-api-key-here")
reviewer.set_provider('openrouter')
reviewer.get_seminar_results()
reviewer.review()

# Update seminar with reviewed results
seminar = reviewer.add_review_results_to_seminar()

# Step 3: Harmonize to reach consensus
print("Step 3: Harmonizing results...")
harmonizer = Harmonizer(seminar)
harmonizer.set_api("your-api-key-here")
harmonizer.set_provider('openrouter')
harmonizer.get_seminar_results()
harmonizer.check()

# Get final consensus
consensus = harmonizer.get_check_result()

print("\nFinal Consensus Results:")
for cluster, result in consensus.items():
    print(f"\n{cluster}:")
    print(f"  Cell Type: {result['consensus_cell_type']}")
    print(f"  Consensus Reached: {result['is_consensus_reached']}")
    print(f"  Agreement: {result['consensus_proportion']*100:.1f}%")
