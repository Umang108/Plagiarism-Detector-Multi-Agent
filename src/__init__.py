"""Plagiarism Detector Core"""
__version__ = "2.0.1"

# Re-export key components
from .config import config, llm, text_embeddings
from .graph import plagiarism_graph
from .processors import load_paper_docs, extract_paper_structure_from_docs
from .search_tools import research_searcher
from .agents import concept_agent, research_agent