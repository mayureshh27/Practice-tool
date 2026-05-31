"""ingestion — public API surface"""
from .chunker import Chunk, Chunker, Strategy
from .extractors import BookExtractor, GitHubExtractor, RawSource, WebExtractor, YouTubeExtractor
from .generator import GeneratedProblem, Generator
from .normaliser import NormalisedDoc, Normaliser
from .pipeline import ExerciseFirstPipeline, IngestionPipeline, RunSummary
from .pipeline_stages import (
                          CatalogMerger,
                          DedupChecker,
                          RetryOrchestrator,
                          ReviewQueue,
                          ValidationResult,
                          Validator,
)
from .structure import BookStructureDetector, StructuredBook

__all__ = [
    "BookExtractor",
    "BookStructureDetector",
    "CatalogMerger",
    "Chunk",
    "Chunker",
    "DedupChecker",
    "ExerciseFirstPipeline",
    "GeneratedProblem",
    "Generator",
    "GitHubExtractor",
    "IngestionPipeline",
    "NormalisedDoc",
    "Normaliser",
    "RawSource",
    "RetryOrchestrator",
    "ReviewQueue",
    "RunSummary",
    "Strategy",
    "StructuredBook",
    "ValidationResult",
    "Validator",
    "WebExtractor",
    "YouTubeExtractor",
]
