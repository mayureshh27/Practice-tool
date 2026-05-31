from __future__ import annotations

from dataclasses import replace

from ..chunker import Chunk
from ..generator import GeneratedProblem, Generator
from .config import MAX_RETRIES, QUALITY_AUTOPASS
from .validator import ValidationResult, Validator


class RetryOrchestrator:
    def __init__(self, generator: Generator, validator: Validator):
        self.gen = generator
        self.val = validator

    def run(self, chunk: Chunk, chapter: str,
            number: int) -> tuple[GeneratedProblem | None, ValidationResult]:

        active_chunk = chunk
        last_problem: GeneratedProblem | None = None
        last_result:  ValidationResult = ValidationResult(False, 0.0)

        for attempt in range(1, MAX_RETRIES + 1):
            print(f"    attempt {attempt}/{MAX_RETRIES}", end=" ")
            try:
                problem = self.gen.generate(active_chunk, chapter, number)
            except Exception as e:
                last_result = ValidationResult(False, 0.0,
                    [f"Schema parse failed: {e}"])
                print("✗ parse error")
                active_chunk = self._augment_chunk(chunk, last_result)
                continue

            result       = self.val.validate(problem)
            last_problem = problem
            last_result  = result

            if result.passed and result.quality_score >= QUALITY_AUTOPASS:
                print(f"✓ quality={result.quality_score:.2f}")
                return problem, result

            if result.errors:
                print(f"✗ errors: {result.errors[0][:60]}")
                active_chunk = self._augment_chunk(chunk, result)
            else:
                print(f"⚠ quality={result.quality_score:.2f} → review")
                return problem, result

        return last_problem, last_result

    @staticmethod
    def _augment_chunk(chunk: Chunk, result: ValidationResult) -> Chunk:
        correction = (
            "\n\n━━━ PREVIOUS ATTEMPT FAILED — FIX ALL ISSUES ━━━\n"
            + "\n".join(f"ERROR: {e}" for e in result.errors)
            + "\n".join(f"WARNING: {w}" for w in result.warnings)
            + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        return replace(chunk, text=chunk.text + correction)
