"""
Test script for MultiLLMc - Seminar + Harmonizer (initial annotations + consensus)
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mllmcelltype import Seminar, Harmonizer


def run_test():
    """Run annotation test with initial results and consensus."""
    
    marker_genes = {
        "cluster_0": ["CD3D", "CD3E", "CD3G", "IL7R", "TCF7"],
        "cluster_1": ["CD79A", "CD79B", "MS4A1", "IGHM", "IGKC"],
        "cluster_2": ["CD14", "LYZ", "S100A8", "S100A9", "FCN1"],
    }
    
    api_key = "sk-VW019xQdJlI0EJKpESIj8UcUYWTMyBop78hsJQ2W5P8ppe3D"
    models = ['grok-3', 'deepseek-v3.2', 'qwen-plus']
    provider = 'n1n'
    
    print("=" * 60)
    print("MultiLLMc Test - Initial Annotations + Consensus")
    print("=" * 60)
    
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
    
    print("\n" + "=" * 60)
    print("[Step 1] Initial Annotations (Seminar)")
    print("=" * 60)
    
    for cluster_id, models_data in cluster_results.items():
        print(f"\n{cluster_id}:")
        for model_name, annotation in models_data.items():
            print(f"  {model_name}: {annotation.get('celltype', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("[Step 2] Consensus Analysis (Harmonizer)")
    print("=" * 60)
    
    seminar.final_review_results = cluster_results
    
    harmonizer = Harmonizer(seminar)
    harmonizer.set_api(api_key)
    harmonizer.set_provider(provider)
    harmonizer.get_seminar_results()
    harmonizer.check()
    
    consensus_results = harmonizer.get_check_result()
    
    for cluster_id, consensus in consensus_results.items():
        print(f"\n{cluster_id}:")
        if consensus:
            print(f"  Consensus: {consensus.get('consensus_cell_type', 'N/A')}")
            print(f"  Proportion: {consensus.get('consensus_proportion', 0):.2%}")
            print(f"  Entropy: {consensus.get('entropy_value', 0):.4f}")
    
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
        results["clusters"][cluster_id] = {
            "cluster_id": cluster_id,
            "marker_genes": marker_genes[cluster_id],
            "initial_annotations": cluster_results.get(cluster_id, {}),
            "consensus": consensus_results.get(cluster_id, {})
        }
    
    output_file = os.path.join(os.path.dirname(__file__), 'test_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print(f"Results saved to: {output_file}")
    print("=" * 60)
    return results


if __name__ == '__main__':
    run_test()
