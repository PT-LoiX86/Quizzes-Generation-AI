"""
Chemistry AI Question Generator Package

This package contains all modules for generating Vietnamese chemistry questions
using templates and LLM enhancement.

Modules:
- utils: Utility functions (rounding, logging, config loading)
- fact_extractor: Parse chemistry data files
- facts_loader: Load facts database CSV
- question_templates: Question template definitions
- deduplicator: Duplicate detection and removal
- llm_client: Ollama/Mistral 7B interface
- question_generator: Main generation orchestrator
- summary_generator: Debug summary generation
- io_handler: Input/output validation
"""

__version__ = "1.0.0"
__author__ = "Chemistry AI Team"

from src.utils import load_config, get_timestamp, log_debug, round_number
from src.fact_extractor import FactExtractor
from src.facts_loader import FactsLoader
from src.question_templates import get_all_templates, generate_question_text
from src.deduplicator import Deduplicator
from src.llm_client import OllamaClient
from src.question_generator import QuestionGenerator
from src.summary_generator import SummaryGenerator

__all__ = [
    'load_config',
    'get_timestamp',
    'log_debug',
    'round_number',
    'FactExtractor',
    'FactsLoader',
    'get_all_templates',
    'generate_question_text',
    'Deduplicator',
    'OllamaClient',
    'QuestionGenerator',
    'SummaryGenerator'
]
