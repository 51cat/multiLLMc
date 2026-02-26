"""
Test script for MultiLLMc with real API
"""

import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mllmcelltype import Seminar, Reviewer, Harmonizer


def run_test():
    """Run full annotation test."""
    
    # Test marker genes - PBMC dataset
    marker_genes = {
        "cluster_0": ["CD3D", "CD3E", "CD3G", "IL7R", "TCF7"],
        "cluster_1": ["CD79A", "CD79B", "MS4A1", "IGHM", "IGKC"],
        "cluster_2": ["CD14", "LYZ", "S100A8", "S100A9", "FCN1"],
        "cluster_3": ["FCGR3A", "NCR1", "KLRD1", "GNLY", "PRF1"],
        "cluster_4": ["PPBP", "PF4", "TUBB1", "GP9", "ITGA2B"],
    }
    
    # API configuration
    api_key = "sk-VW019xQdJlI0EJKpESIj8UcUYWTMyBop78hsJQ2W5P8ppe3D"
    models = ['grok-3', 'deepseek-v3.2', 'qwen-plus']
    provider = 'n1n'
    
    print("=" * 60)
    print("MultiLLMc Test - Multi-Model Cell Type Annotation")
    print("=" * 60)
    print(f"Models: {models}")
    print(f"Provider: {provider}")
    print(f"Clusters: {list(marker_genes.keys())}")
    print("=" * 60)
    
    # Step 1: Seminar - Multi-model annotation
    print("\n[Step 1] Running Seminar - Multi-model annotation...")
    
    seminar = Seminar(
        marker_dict=marker_genes,
        species='human',
        tissue='PBMC'
    )
    
    seminar.set_api(api_key)
    seminar.set_provider(provider)
    seminar.set_model_list(models)
    seminar.make_init_ann_promopt('major_celltype')
    seminar.start()
    
    cluster_results = seminar.get_cluster_results()
    print(f"\nSeminar completed. Results for {len(cluster_results)} clusters.")
    
    # Step 2: Review - Quality audit
    print("\n[Step 2] Running Reviewer - Quality audit...")
    
    reviewer = Reviewer(seminar)
    reviewer.set_api(api_key)
    reviewer.set_provider(provider)
    reviewer.get_seminar_results()
    reviewer.review()
    
    seminar = reviewer.add_review_results_to_seminar()
    print("Review completed.")
    
    # Step 3: Harmonize - Consensus building
    print("\n[Step 3] Running Harmonizer - Consensus building...")
    
    harmonizer = Harmonizer(seminar)
    harmonizer.set_api(api_key)
    harmonizer.set_provider(provider)
    harmonizer.get_seminar_results()
    harmonizer.check()
    
    consensus = harmonizer.get_check_result()
    print(f"Harmonization completed. Consensus for {len(consensus)} clusters.")
    
    # Prepare final results
    results = {
        "metadata": {
            "species": "human",
            "tissue": "PBMC",
            "models": models,
            "provider": provider
        },
        "clusters": {}
    }
    
    for cluster_id in marker_genes.keys():
        cluster_data = {
            "cluster_id": cluster_id,
            "marker_genes": marker_genes[cluster_id],
            "model_annotations": seminar.final_review_results.get(cluster_id, {}),
            "consensus": consensus.get(cluster_id, {})
        }
        results["clusters"][cluster_id] = cluster_data
    
    # Save results
    output_file = os.path.join(os.path.dirname(__file__), 'test_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\nResults saved to: {output_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    for cluster_id, data in results["clusters"].items():
        consensus_data = data.get("consensus", {})
        cell_type = consensus_data.get("consensus_cell_type", "Unknown")
        proportion = consensus_data.get("consensus_proportion", 0)
        print(f"{cluster_id}: {cell_type} (agreement: {proportion*100:.1f}%)")
    
    return results


if __name__ == '__main__':
    results = run_test()
