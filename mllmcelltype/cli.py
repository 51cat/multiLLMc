"""
Command Line Interface for MultiLLMc.
"""

import argparse
import json
import sys
from typing import Dict, List

from mllmcelltype import Seminar, Reviewer, Harmonizer


def parse_marker_file(filepath: str) -> Dict[str, List[str]]:
    """Parse marker genes from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def main():
    parser = argparse.ArgumentParser(
        description='Multi-LLM Collaborative Cell Type Annotation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  multillmc annotate --markers markers.json --api-key KEY --provider n1n --models gpt-4o,claude-3-sonnet
  multillmc annotate --markers markers.json --species human --tissue PBMC --output results.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Annotate command
    annotate_parser = subparsers.add_parser('annotate', help='Annotate cell types')
    annotate_parser.add_argument('--markers', '-m', required=True, help='JSON file with marker genes')
    annotate_parser.add_argument('--api-key', '-k', required=True, help='API key')
    annotate_parser.add_argument('--provider', '-p', default='n1n', help='API provider (default: n1n)')
    annotate_parser.add_argument('--models', required=True, help='Comma-separated list of models')
    annotate_parser.add_argument('--species', default='human', help='Species (default: human)')
    annotate_parser.add_argument('--tissue', default='PBMC', help='Tissue type (default: PBMC)')
    annotate_parser.add_argument('--tissue-desc', default='', help='Tissue description')
    annotate_parser.add_argument('--output', '-o', default=None, help='Output JSON file')
    annotate_parser.add_argument('--review', action='store_true', help='Enable review step')
    annotate_parser.add_argument('--harmonize', action='store_true', help='Enable harmonize step')
    
    # List providers
    providers_parser = subparsers.add_parser('providers', help='List available providers')
    
    args = parser.parse_args()
    
    if args.command == 'providers':
        from mllmcelltype._provider import URL_DICT
        print("Available providers:")
        for name, url in URL_DICT.items():
            print(f"  - {name}: {url}")
        return
    
    if args.command == 'annotate':
        # Parse markers
        markers = parse_marker_file(args.markers)
        models = [m.strip() for m in args.models.split(',')]
        
        # Initialize seminar
        seminar = Seminar(
            marker_dict=markers,
            species=args.species,
            tissue=args.tissue,
            tissue_desc=args.tissue_desc
        )
        
        # Configure
        seminar.set_api(args.api_key)
        seminar.set_provider(args.provider)
        seminar.set_model_list(models)
        
        # Run annotation
        print("Starting annotation...")
        seminar.make_init_ann_promopt('major_celltype')
        seminar.start()
        
        results = seminar.get_cluster_results()
        
        # Optional review
        if args.review:
            print("Running review...")
            reviewer = Reviewer(seminar)
            reviewer.set_api(args.api_key)
            reviewer.set_provider(args.provider)
            reviewer.get_seminar_results()
            reviewer.review()
            results = reviewer.review_final_results
        
        # Optional harmonize
        if args.harmonize:
            print("Running harmonization...")
            harmonizer = Harmonizer(seminar)
            harmonizer.set_api(args.api_key)
            harmonizer.set_provider(args.provider)
            harmonizer.get_seminar_results()
            harmonizer.check()
            consensus = harmonizer.get_check_result()
            results['consensus'] = consensus
        
        # Output
        output_json = json.dumps(results, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_json)
            print(f"Results saved to {args.output}")
        else:
            print(output_json)
        
        return
    
    parser.print_help()


if __name__ == '__main__':
    main()
