"""
ingestion/generation/pipeline_stages.py
========================================
Stages 4–8 of the ingestion pipeline:

  4. Validator      — schema OK + Python syntax + sandbox test + quality score
  5. RetryOrchestrator — up to MAX_RETRIES with error feedback
  6. DedupChecker   — cosine similarity + slug uniqueness
  7. ReviewQueue    — CLI approve / edit / reject / skip
  8. CatalogMerger  — atomic JSON write + optional git commit

Design: each stage is a plain class, no framework magic.
You can call them independently for debugging.
"""

from __future__ import annotations
import ast, json, os, re, subprocess, tempfile, uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
from sentence_transformers import SentenceTransformer

from .generator import GeneratedProblem, Generator
from ..processing.chunker import Chunk

# ─────────────────────────────────────────────────────────────────────────────
# Config constants
# ─────────────────────────────────────────────────────────────────────────────

CATALOG_PATH     = Path("data/problems.json")
SANDBOX_IMAGE    = os.getenv("GOPRAC_SANDBOX_IMAGE", "learning-platform:python")
SANDBOX_BIN      = os.getenv("GOPRAC_SANDBOX_BIN",   "docker")
EMBED_MODEL      = "all-MiniLM-L6-v2"
DEDUP_THRESHOLD  = 0.88     # cosine similarity above → duplicate
QUALITY_AUTOPASS = 0.82     # skip human review
MAX_RETRIES      = 3


# ─────────────────────────────────────────────────────────────────────────────
# 4. VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    passed:        bool
    quality_score: float          # 0.0 – 1.0
    errors:        list[str] = field(default_factory=list)
    warnings:      list[str] = field(default_factory=list)


class Validator:
    """
    Four-pass validation:
      A. Pydantic schema — guaranteed by Instructor, but we re-check edge cases
      B. Python syntax   — ast.parse on all three code fields
      C. Sandbox run     — actually execute testCode inside Docker/local
      D. Quality heuristic — content richness scoring
    """

    def validate(self, p: GeneratedProblem) -> ValidationResult:
        errors:   list[str] = []
        warnings: list[str] = []

        # Pass B: Python syntax
        for attr in ("starterCode", "solutionCode", "testCode"):
            code = getattr(p, attr)
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append(f"{attr} syntax error L{e.lineno}: {e.msg}")

        if errors:
            return ValidationResult(False, 0.0, errors, warnings)

        # Pass C: sandbox execution
        ok, msg = self._sandbox_run(p.solutionCode, p.testCode)
        if not ok:
            errors.append(f"Sandbox: {msg[:400]}")
            return ValidationResult(False, 0.0, errors, warnings)

        # Pass D: quality
        score = self._quality(p, warnings)
        return ValidationResult(True, score, errors, warnings)

    # ── Sandbox ───────────────────────────────────────────────────────────────

    @staticmethod
    def _sandbox_run(solution: str, tests: str) -> tuple[bool, str]:
        """
        Combine solution + tests into one file and run in Docker.
        Falls back to in-process exec() if Docker not available.
        """
        combined = (
            solution.strip()
            + "\n\n# ── harness test ──────────────────────────\n"
            + tests.strip()
        )
        try:
            import shutil
            runtime = shutil.which(SANDBOX_BIN)

            if runtime:
                with tempfile.TemporaryDirectory() as tmp:
                    src = Path(tmp) / "solution.py"
                    src.write_text(combined)
                    result = subprocess.run(
                        [
                            runtime, "run", "--rm",
                            "--network",    "none",
                            "--memory",     "256m",
                            "--cpus",       "0.5",
                            "--pids-limit", "32",
                            "--read-only",
                            "--tmpfs",      "/tmp:rw,nosuid,nodev,size=64m",
                            "--security-opt", "no-new-privileges",
                            "--cap-drop",   "ALL",
                            "--user",       "65532:65532",
                            "-e", "PYTHONDONTWRITEBYTECODE=1",
                            "-v", f"{tmp}:/workspace:ro",
                            "-w", "/workspace",
                            SANDBOX_IMAGE,
                            "python3", "solution.py",
                        ],
                        capture_output=True, text=True, timeout=20,
                    )
                    if result.returncode == 0:
                        return True, result.stdout
                    return False, (result.stderr + result.stdout).strip()

            # No Docker — run inline (trusted environment only)
            return Validator._inline_run(combined)

        except subprocess.TimeoutExpired:
            return False, "Timed out (>20 s)"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _inline_run(code: str) -> tuple[bool, str]:
        import io, contextlib
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(code, "<generated>", "exec"), {})  # noqa: S102
            return True, buf.getvalue()
        except Exception as e:
            return False, str(e)

    # ── Quality heuristic ─────────────────────────────────────────────────────

    @staticmethod
    def _quality(p: GeneratedProblem, warnings: list[str]) -> float:
        score = 1.0

        # Explanation richness
        exp_words = len(p.explanation.split())
        if exp_words < 200:
            score -= 0.20
            warnings.append(f"explanation thin ({exp_words} words; aim ≥200)")

        # Must have a "Common mistakes" section for maths problems
        if any(t in ["math", "algebra", "calculus", "probability",
                     "linear_algebra", "statistics"]
               for t in p.tags):
            if "common mistake" not in p.explanation.lower():
                score -= 0.15
                warnings.append("maths problem missing 'Common mistakes' section")

        # Solution code richness
        sol_lines = [l for l in p.solutionCode.splitlines() if l.strip()]
        if len(sol_lines) < 3:
            score -= 0.15
            warnings.append("solution code trivially short")

        # Test coverage
        assert_count = p.testCode.count("assert ")
        if assert_count < 3:
            score -= 0.10
            warnings.append(f"only {assert_count} assertions; aim ≥3")

        # Examples
        if not p.examples:
            score -= 0.10
            warnings.append("no examples provided")

        # Prerequisites filled in
        if not p.prerequisites:
            warnings.append("prerequisites empty — fill manually if relevant")

        return round(max(0.0, score), 3)


# ─────────────────────────────────────────────────────────────────────────────
# 5. RETRY ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────────────────

class RetryOrchestrator:
    """
    Drive generate → validate → retry loop.
    On each failure the full error list is appended to the chunk text
    as a correction block so the model can self-heal.
    """

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
                print(f"✗ parse error")
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
                # Passed validation, below auto-pass — send to review
                print(f"⚠ quality={result.quality_score:.2f} → review")
                return problem, result

        return last_problem, last_result

    @staticmethod
    def _augment_chunk(chunk: Chunk, result: ValidationResult) -> Chunk:
        """Append error context to chunk so next attempt knows what failed."""
        from dataclasses import replace
        correction = (
            "\n\n━━━ PREVIOUS ATTEMPT FAILED — FIX ALL ISSUES ━━━\n"
            + "\n".join(f"ERROR: {e}" for e in result.errors)
            + "\n".join(f"WARNING: {w}" for w in result.warnings)
            + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        return Chunk(
            text          = chunk.text + correction,
            chapter_title = chunk.chapter_title,
            section_title = chunk.section_title,
            chapter_num   = chunk.chapter_num,
            word_count    = chunk.word_count,
            has_math      = chunk.has_math,
            has_code      = chunk.has_code,
            has_theorem   = chunk.has_theorem,
            has_exercise  = chunk.has_exercise,
            source_type   = chunk.source_type,
            metadata      = chunk.metadata,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 6. DEDUP CHECKER
# ─────────────────────────────────────────────────────────────────────────────

class DedupChecker:
    """
    Two-pass deduplication:
      Pass A — cosine similarity of statement embedding vs existing catalog
      Pass B — slug (id) uniqueness

    The embedder runs locally (sentence-transformers, no API call).
    First call is slow (model load ~2s); subsequent calls ~15ms.
    """

    def __init__(self, catalog: dict):
        self._embedder  = SentenceTransformer(EMBED_MODEL)
        self._ids       = {p["id"] for p in catalog.get("problems", [])}
        statements      = [p.get("statement", "")
                           for p in catalog.get("problems", [])]
        self._embeddings: np.ndarray | None = None
        if statements:
            self._embeddings = self._embedder.encode(
                statements, normalize_embeddings=True, show_progress_bar=False
            )

    def is_duplicate(self, p: GeneratedProblem) -> tuple[bool, str]:
        # Pass B: cheap slug check first
        if p.id in self._ids:
            return True, f"slug collision: '{p.id}' already exists"

        # Pass A: semantic similarity
        if self._embeddings is not None and len(self._embeddings) > 0:
            new_emb = self._embedder.encode(
                [p.statement], normalize_embeddings=True,
                show_progress_bar=False
            )
            sims    = (self._embeddings @ new_emb.T).squeeze()
            max_sim = float(np.max(sims))
            if max_sim >= DEDUP_THRESHOLD:
                idx = int(np.argmax(sims))
                return (
                    True,
                    f"cosine={max_sim:.3f} ≥ {DEDUP_THRESHOLD} "
                    f"vs existing problem at index {idx}"
                )
        return False, ""

    def register(self, p: GeneratedProblem):
        """Add accepted problem to in-memory index for intra-run dedup."""
        self._ids.add(p.id)
        new_emb = self._embedder.encode(
            [p.statement], normalize_embeddings=True, show_progress_bar=False
        )
        self._embeddings = (
            new_emb if self._embeddings is None
            else np.vstack([self._embeddings, new_emb])
        )


# ─────────────────────────────────────────────────────────────────────────────
# 7. REVIEW QUEUE
# ─────────────────────────────────────────────────────────────────────────────

class ReviewQueue:
    """
    Interactive CLI review for problems below QUALITY_AUTOPASS or with warnings.

    Actions:
      a / approve  — accept as-is
      e / edit     — open JSON in $EDITOR, re-validate on save
      r / reject   — discard
      s / skip     — write to pending_review.json, decide later
      v / view     — print full problem JSON then ask again
    """

    PENDING_PATH = Path("data/pending_review.json")

    def __init__(self, validator: Validator):
        self.validator = validator
        self.approved: list[GeneratedProblem] = []
        self.rejected: list[str]              = []
        self.pending:  list[dict]             = []

    def review(self, p: GeneratedProblem, result: ValidationResult):
        # Auto-approve high quality with no errors
        if result.passed and result.quality_score >= QUALITY_AUTOPASS \
                and not result.errors:
            self.approved.append(p)
            return

        # Auto-reject if validation still failing after all retries
        if not result.passed:
            print(f"  ✗ AUTO-REJECT {p.id}: {'; '.join(result.errors[:2])}")
            self.rejected.append(p.id)
            return

        # Human review
        self._display_summary(p, result)
        while True:
            raw = input("  Action [a]pprove [e]dit [r]eject [s]kip [v]iew: ").strip().lower()
            action = raw[0] if raw else "s"
            if action == "a":
                self.approved.append(p)
                break
            elif action == "e":
                edited = self._open_editor(p)
                if edited:
                    re_result = self.validator.validate(edited)
                    if re_result.passed:
                        self.approved.append(edited)
                        print(f"  ✓ Approved after edit (quality={re_result.quality_score:.2f})")
                    else:
                        print(f"  ✗ Re-validation failed: {re_result.errors}")
                        self.pending.append(edited.model_dump())
                break
            elif action == "r":
                self.rejected.append(p.id)
                break
            elif action == "s":
                self.pending.append(p.model_dump())
                break
            elif action == "v":
                print(json.dumps(p.model_dump(), indent=2)[:3000])
            else:
                print("  Unknown action. Try a/e/r/s/v")

    def flush_pending(self):
        if not self.pending:
            return
        self.PENDING_PATH.parent.mkdir(parents=True, exist_ok=True)
        existing = []
        if self.PENDING_PATH.exists():
            existing = json.loads(self.PENDING_PATH.read_text())
        self.PENDING_PATH.write_text(
            json.dumps(existing + self.pending, indent=2)
        )
        print(f"  📋 {len(self.pending)} problems written to {self.PENDING_PATH}")

    @staticmethod
    def _display_summary(p: GeneratedProblem, r: ValidationResult):
        bar = "█" * int(r.quality_score * 20) + "░" * (20 - int(r.quality_score * 20))
        print(f"\n  ┌─ {p.title}")
        print(f"  │  id={p.id}  chapter={p.chapter}  difficulty={p.difficulty}")
        print(f"  │  quality=[{bar}] {r.quality_score:.2f}")
        if r.warnings:
            print(f"  │  warnings: {', '.join(r.warnings[:3])}")
        print(f"  └─ tags: {', '.join(p.tags[:5])}")

    @staticmethod
    def _open_editor(p: GeneratedProblem) -> GeneratedProblem | None:
        editor = os.getenv("EDITOR", "nano")
        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False, encoding="utf-8"
        ) as f:
            json.dump(p.model_dump(), f, indent=2, ensure_ascii=False)
            fname = f.name
        subprocess.run([editor, fname])
        try:
            data = json.loads(Path(fname).read_text())
            return GeneratedProblem(**data)
        except Exception as e:
            print(f"  Parse error after edit: {e}")
            return None
        finally:
            Path(fname).unlink(missing_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 8. CATALOG MERGER
# ─────────────────────────────────────────────────────────────────────────────

class CatalogMerger:
    """
    Merge approved problems into problems.json.

    Steps:
      1. Load existing catalog (or create empty one)
      2. Ensure chapter exists in catalog["chapters"]
      3. Assign globally unique problem numbers
      4. Atomic write: write to .tmp, then rename
      5. Optional git commit with descriptive message
    """

    def __init__(self, catalog_path: Path = CATALOG_PATH):
        self.path = catalog_path

    def merge(self, approved: list[GeneratedProblem],
              chapter_id: str, chapter_title: str,
              auto_commit: bool = False):
        if not approved:
            print("  No problems to merge.")
            return

        # Load or create catalog
        if self.path.exists():
            catalog = json.loads(self.path.read_text())
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            catalog = {"chapters": [], "problems": []}

        # Ensure chapter registered
        ch_ids = {c["id"] for c in catalog["chapters"]}
        if chapter_id not in ch_ids:
            catalog["chapters"].append(
                {"id": chapter_id, "title": chapter_title}
            )
            print(f"  + Added chapter: {chapter_id} — {chapter_title}")

        # Number from current max
        existing_max = max(
            (p.get("number", 0) for p in catalog["problems"]), default=0
        )
        new_dicts = []
        for i, p in enumerate(approved):
            d = p.model_dump()
            d["number"] = existing_max + i + 1
            new_dicts.append(d)

        catalog["problems"].extend(new_dicts)

        # Atomic write
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
        tmp.replace(self.path)

        print(f"  ✓ Merged {len(approved)} problems")
        print(f"    Catalog: {len(catalog['problems'])} problems "
              f"across {len(catalog['chapters'])} chapters")

        if auto_commit:
            self._git_commit(chapter_id, len(approved))

    def _git_commit(self, chapter_id: str, count: int):
        try:
            subprocess.run(
                ["git", "add", str(self.path)],
                check=True, capture_output=True
            )
            from datetime import datetime, timezone
            msg = (
                f"harness: add {count} problems to {chapter_id}\n\n"
                f"Generated {datetime.now(timezone.utc).isoformat()}"
            )
            subprocess.run(
                ["git", "commit", "-m", msg],
                check=True, capture_output=True
            )
            print("  ↳ git commit created")
        except subprocess.CalledProcessError:
            print("  ↳ git commit skipped")
