# MultiLLMc

Multi-LLM Collaborative Cell Type Annotation for Single-Cell RNA-seq

A framework that uses multiple large language models to collaboratively annotate cell types in single-cell RNA sequencing data.

## Features

- **Multi-LLM Discussion**: Leverage multiple LLMs to discuss and annotate cell types
- **Quality Review**: Built-in review mechanism to audit and correct annotations
- **Consensus Building**: Harmonize results from multiple models to reach consensus
- **Flexible Provider Support**: Support for various API providers (n1n, openrouter)

## Installation

```bash
pip install multillmc
```

Or install from source:

```bash
git clone https://github.com/51cat/multiLLMc.git
cd multiLLMc
pip install -e .
```

## Quick Start

```python
from mllmcelltype import Seminar, Reviewer, Harmonizer

# Define marker genes for each cluster
marker_genes = {
    "cluster_0": ["CD3D", "CD3E", "CD3G", "IL7R", "TCF7"],
    "cluster_1": ["CD79A", "CD79B", "MS4A1", "IGHM", "IGKC"],
    "cluster_2": ["CD14", "LYZ", "S100A8", "S100A9", "FCN1"],
}

# Initialize seminar
seminar = Seminar(
    marker_dict=marker_genes,
    species='human',
    tissue='PBMC'
)

# Configure API and models
seminar.set_api("your-api-key")
seminar.set_model_list(['gpt-4o', 'claude-3-sonnet', 'gemini-pro'])
seminar.set_provider('openrouter')

# Run annotation
seminar.make_init_ann_promopt('major_celltype')
seminar.start()

# Get results
cluster_results = seminar.get_cluster_results()

# Optional: Review and harmonize
reviewer = Reviewer(seminar)
reviewer.set_api("your-api-key")
reviewer.set_provider('openrouter')
reviewer.get_seminar_results()
reviewer.review()

harmonizer = Harmonizer(seminar)
harmonizer.set_api("your-api-key")
harmonizer.set_provider('openrouter')
harmonizer.get_seminar_results()
harmonizer.check()
consensus = harmonizer.get_check_result()
```

## Workflow

1. **Seminar**: Multiple LLMs independently annotate cell types based on marker genes
2. **Review**: Audit annotations for quality, detect hallucinations, and correct errors
3. **Harmonize**: Build consensus from multiple model predictions

## API Providers

Supported providers:
- `n1n`: N1N API Gateway
- `openrouter`: OpenRouter unified API

## Requirements

- Python >= 3.10
- langchain >= 0.2.0
- langchain-openai >= 0.1.0
- pydantic >= 2.0.0
- jinja2 >= 3.1.0

## License

MIT License

## Author

51cat
