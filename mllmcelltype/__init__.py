"""
Multi-LLM Collaborative Cell Type Annotation for Single-Cell RNA-seq

A framework that uses multiple large language models to collaboratively 
annotate cell types in single-cell RNA sequencing data.
"""

__version__ = "0.1.0"
__author__ = "51cat"

from mllmcelltype.seminar import Seminar
from mllmcelltype.reviewer import Reviewer
from mllmcelltype.harmonizer import Harmonizer

__all__ = ["Seminar", "Reviewer", "Harmonizer"]
