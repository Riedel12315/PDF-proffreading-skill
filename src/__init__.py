"""
PDF Proofreading Tool
智能PDF文档校对工具
"""

__version__ = "1.0.0"
__author__ = "Qing Shao"
__email__ = "your.email@example.com"

from .proofreader import Proofreader
from .grammar_checker import GrammarChecker
from .pdf_annotator import PDFAnnotator
from .report_generator import ReportGenerator

__all__ = [
    "Proofreader",
    "GrammarChecker", 
    "PDFAnnotator",
    "ReportGenerator",
]