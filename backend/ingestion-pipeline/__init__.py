"""ingestion — public API surface"""
from .pipeline import IngestionPipeline, ExerciseFirstPipeline, RunSummary
from .sources.extractors import (BookExtractor, GitHubExtractor,
                                  YouTubeExtractor, WebExtractor, RawSource)
from .processing.normaliser import Normaliser, NormalisedDoc
from .processing.chunker    import Chunker, Chunk, Strategy
from .processing.structure  import BookStructureDetector, StructuredBook
from .generation.generator  import Generator, GeneratedProblem
from .generation.pipeline_stages import (Validator, ValidationResult,
                                          RetryOrchestrator, DedupChecker,
                                          ReviewQueue, CatalogMerger)
