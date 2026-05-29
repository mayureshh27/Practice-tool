"""
tests/test_ingestion.py
========================
Integration tests for every pipeline stage.

These tests use NO external API calls — they mock the LLM layer
and test the pipeline logic, parsing, chunking, validation, and dedup.

Run: pytest tests/test_ingestion.py -v

Fast tests (no model calls, no Docker):
  test_normaliser_*
  test_chunker_*
  test_structure_*
  test_dedup_*
  test_validator_syntax_*

Slow tests (require Docker sandbox):
  test_validator_sandbox_*   -- mark: @pytest.mark.slow

End-to-end tests (require API key in env):
  test_e2e_*                 -- mark: @pytest.mark.e2e
"""

from __future__ import annotations
import json, re, textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

SAMPLE_MATH_TEXT = textwrap.dedent("""
    # Chapter 3: Eigenvalues and Eigenvectors

    ## 3.1 Definition

    Let $A$ be an $n \\times n$ matrix. A scalar $\\lambda$ is called an
    **eigenvalue** of $A$ if there exists a nonzero vector $\\mathbf{v}$ such that

    $$A\\mathbf{v} = \\lambda \\mathbf{v}$$

    The vector $\\mathbf{v}$ is called an **eigenvector** corresponding to $\\lambda$.

    Theorem 3.1: The eigenvalues of $A$ are the roots of the characteristic
    polynomial $p(\\lambda) = \\det(A - \\lambda I)$.

    Proof: $A\\mathbf{v} = \\lambda\\mathbf{v}$ means $(A - \\lambda I)\\mathbf{v} = 0$
    has a nonzero solution, which requires $\\det(A - \\lambda I) = 0$. □

    ## 3.2 Computing Eigenvalues

    Example 3.1: Find the eigenvalues of $A = \\begin{pmatrix} 2 & 1 \\\\ 1 & 2 \\end{pmatrix}$.

    Solution: $p(\\lambda) = (2 - \\lambda)^2 - 1 = \\lambda^2 - 4\\lambda + 3
    = (\\lambda - 1)(\\lambda - 3)$

    So $\\lambda_1 = 1$ and $\\lambda_2 = 3$.

    ## Exercises

    Exercise 3.1: Find the eigenvalues and eigenvectors of
    $B = \\begin{pmatrix} 3 & -2 \\\\ 1 & 0 \\end{pmatrix}$.
    (Hint: characteristic polynomial is $\\lambda^2 - 3\\lambda + 2$)

    Exercise 3.2: Show that if $\\lambda$ is an eigenvalue of $A$ with eigenvector
    $\\mathbf{v}$, then $\\lambda^2$ is an eigenvalue of $A^2$ with the same eigenvector.
""").strip()

SAMPLE_CODE_TEXT = textwrap.dedent("""
    # NumPy Broadcasting

    ## Core Concept

    Broadcasting allows NumPy to perform operations on arrays of different shapes.

    ```python
    import numpy as np

    # Shape (3,) + scalar
    a = np.array([1, 2, 3])
    b = a + 10      # [11, 12, 13]

    # Shape (3, 1) + (3,)
    col = np.array([[1], [2], [3]])
    row = np.array([10, 20, 30])
    result = col + row   # (3, 3) matrix
    ```

    The rule: dimensions are compared right-to-left.
    A dimension of size 1 is stretched to match the other.
""").strip()

MINIMAL_VALID_PROBLEM = {
    "id":           "test-eigenvalue-basic",
    "number":       1,
    "title":        "Exercise 3.1: Basic Eigenvalues",
    "chapter":      "la3",
    "difficulty":   "medium",
    "tags":         ["eigenvalues", "linear_algebra", "numpy"],
    "exerciseMode": "judge",
    "verifier":     "local-tests",
    "statement":    "Find the eigenvalues of a 2x2 matrix.",
    "problemText":  "Given a 2x2 numpy array A, return its eigenvalues sorted ascending.",
    "explanation":  textwrap.dedent("""
        ### What you are learning
        Eigenvalues tell you how a matrix scales space.

        ### The intuition
        An eigenvector is a direction unchanged by the matrix transformation.
        The eigenvalue is the scaling factor in that direction.

        ### Common mistakes
        Using np.linalg.eig without sorting the output.
        Forgetting that eig returns complex numbers for non-symmetric matrices.

        ### Mental model check
        For a 2x2 matrix the eigenvalues are the roots of a quadratic.
        Check: trace(A) == λ1 + λ2 and det(A) == λ1 * λ2.
    """).strip(),
    "howItWorks":   "Compute characteristic polynomial, find roots.",
    "syntax":       "np.linalg.eig(A) returns (eigenvalues, eigenvectors)",
    "solve":        "Use np.linalg.eig, sort the eigenvalue array.",
    "hints": [
        "What equation must λ satisfy for Av=λv to have a nonzero solution?",
        "np.linalg.eig returns eigenvalues in arbitrary order — what should you do with them?",
        "For a symmetric matrix, are eigenvalues always real? Why does that matter here?",
    ],
    "starterCode": textwrap.dedent("""
        import numpy as np

        def solve(A):
            # A is a 2x2 numpy array
            # Return eigenvalues as a sorted numpy array (ascending)
            pass
    """).strip(),
    "solutionCode": textwrap.dedent("""
        import numpy as np

        def solve(A):
            eigenvalues, _ = np.linalg.eig(A)
            return np.sort(eigenvalues.real)
    """).strip(),
    "testCode": textwrap.dedent("""
        from solution import solve
        import numpy as np

        # Identity matrix: eigenvalues both 1
        A1 = np.eye(2)
        result = solve(A1)
        assert np.allclose(result, [1.0, 1.0]), f"Expected [1,1] got {result}"

        # Diagonal matrix
        A2 = np.array([[3.0, 0.0], [0.0, 1.0]])
        result = solve(A2)
        assert np.allclose(result, [1.0, 3.0]), f"Expected [1,3] got {result}"

        # Strang example matrix
        A3 = np.array([[2.0, 1.0], [1.0, 2.0]])
        result = solve(A3)
        assert np.allclose(result, [1.0, 3.0]), f"Expected [1,3] got {result}"

        print('All tests passed.')
    """).strip(),
    "examples": [
        {"input": "A=[[2,1],[1,2]]", "output": "[1.0, 3.0]"},
    ],
    "prerequisites": ["matrix_mult", "dot_product"],
    "mathConcepts":  ["eigenvalue", "characteristic_polynomial"],
    "sourceRef":     "Strang §6.1",
}


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Normaliser tests
# ─────────────────────────────────────────────────────────────────────────────

class TestNormaliser:

    def test_math_display_tagged(self):
        from ingestion.processing.normaliser import Normaliser
        doc = Normaliser.normalise("Here is $$Av = \\lambda v$$", "book")
        assert doc.has_math
        assert "⟨MATH_DISPLAY⟩" in doc.text

    def test_math_inline_tagged(self):
        from ingestion.processing.normaliser import Normaliser
        doc = Normaliser.normalise("The value $\\lambda$ is real.", "book")
        assert doc.has_math
        assert "⟨MATH_INLINE⟩" in doc.text

    def test_code_fence_tagged(self):
        from ingestion.processing.normaliser import Normaliser
        doc = Normaliser.normalise("```python\nimport numpy\n```", "book")
        assert doc.has_code
        assert "⟨CODE_BLOCK lang=python⟩" in doc.text

    def test_ligature_repair(self):
        from ingestion.processing.normaliser import Normaliser
        doc = Normaliser.normalise("efficient ﬁnally ﬂow", "book")
        assert "ﬁ" not in doc.text
        assert "fi" in doc.text
        assert "fl" in doc.text

    def test_page_numbers_removed(self):
        from ingestion.processing.normaliser import Normaliser
        text = "Some content\n\n42\n\nMore content"
        doc  = Normaliser.normalise(text, "book")
        lines = [l for l in doc.text.splitlines() if l.strip() == "42"]
        assert not lines, "Page number 42 should be removed"

    def test_running_headers_removed(self):
        from ingestion.processing.normaliser import Normaliser
        # Line appearing 4 times — should be stripped
        repeated = "Introduction to Linear Algebra"
        text = "\n\n".join([
            f"{repeated}\n\nSection {i} content with enough words here"
            for i in range(4)
        ])
        doc = Normaliser.normalise(text, "book")
        occurrences = doc.text.count(repeated)
        assert occurrences < 4, "Running header should be reduced"

    def test_theorem_tagged(self):
        from ingestion.processing.normaliser import Normaliser
        doc = Normaliser.normalise(
            "Theorem 3.1: Every symmetric matrix has real eigenvalues.\n\n",
            "book"
        )
        assert doc.has_theorems

    def test_exercise_tagged(self):
        from ingestion.processing.normaliser import Normaliser
        doc = Normaliser.normalise(
            "Exercise 1: Find the dot product of u and v.\n\n",
            "book"
        )
        assert doc.has_exercises

    def test_heading_normalised(self):
        from ingestion.processing.normaliser import Normaliser
        doc = Normaliser.normalise("3.2 Eigenvalue Decomposition\n\nContent.", "book")
        assert "## Eigenvalue Decomposition" in doc.text

    def test_youtube_no_math_tags(self):
        from ingestion.processing.normaliser import Normaliser
        transcript = "So today we talk about vectors and how they scale"
        doc = Normaliser.normalise(transcript, "youtube")
        assert not doc.has_math


# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: Structure detector tests
# ─────────────────────────────────────────────────────────────────────────────

class TestStructureDetector:

    def test_chapter_detection(self):
        from ingestion.processing.normaliser import Normaliser
        from ingestion.processing.structure  import BookStructureDetector
        doc  = Normaliser.normalise(SAMPLE_MATH_TEXT, "book")
        book = BookStructureDetector.detect(doc.text, title="Test")
        assert len(book.chapters) >= 1

    def test_exercise_extraction(self):
        from ingestion.processing.normaliser import Normaliser
        from ingestion.processing.structure  import BookStructureDetector
        doc  = Normaliser.normalise(SAMPLE_MATH_TEXT, "book")
        book = BookStructureDetector.detect(doc.text, title="Test")
        total = book.total_exercises
        assert total >= 1, f"Expected ≥1 exercise, found {total}"

    def test_theorem_extraction(self):
        from ingestion.processing.normaliser import Normaliser
        from ingestion.processing.structure  import BookStructureDetector
        doc  = Normaliser.normalise(SAMPLE_MATH_TEXT, "book")
        book = BookStructureDetector.detect(doc.text, title="Test")
        assert book.total_theorems >= 1

    def test_hint_extracted_from_exercise(self):
        from ingestion.processing.structure import BookStructureDetector
        text = """
## Exercises

Exercise 1: Find eigenvalues of A. (Hint: use characteristic polynomial)
"""
        book = BookStructureDetector.detect(text, "Test")
        all_ex = [e for c in book.chapters for t in c.topics for e in t.exercises]
        hints  = [e.hint for e in all_ex if e.hint]
        assert hints, "Should extract hint from exercise"

    def test_difficulty_gradient(self):
        from ingestion.processing.structure import BookStructureDetector
        text = "\n\n".join([
            f"# Chapter {i}\n\nContent for chapter {i} with enough words."
            for i in range(6)
        ])
        book = BookStructureDetector.detect(text, "Test")
        diffs = [c.difficulty_hint for c in book.chapters]
        assert "easy" in diffs
        assert "hard" in diffs


# ─────────────────────────────────────────────────────────────────────────────
# Stage 4: Chunker tests
# ─────────────────────────────────────────────────────────────────────────────

class TestChunker:

    def test_hierarchical_produces_chunks(self):
        from ingestion.processing.normaliser import Normaliser
        from ingestion.processing.chunker    import Chunker, Strategy
        doc    = Normaliser.normalise(SAMPLE_MATH_TEXT, "book")
        chunks = Chunker().chunk(doc, Strategy.HIERARCHICAL)
        assert len(chunks) >= 1

    def test_no_split_inside_math_display(self):
        from ingestion.processing.normaliser import Normaliser
        from ingestion.processing.chunker    import Chunker, Strategy
        # One huge display math block that exceeds max_words
        big_math = "⟨MATH_DISPLAY⟩\n" + "word " * 1200 + "\n⟨/MATH_DISPLAY⟩"
        doc  = Normaliser.normalise(big_math, "book")
        # Override: inject pre-tagged text
        doc.text = big_math
        chunks = Chunker(max_words=200).chunk(doc, Strategy.FLAT_SEMANTIC)
        # If any chunk starts with MATH_DISPLAY it means we split into it
        # — we want all chunks to either contain the full block or none
        for c in chunks:
            opens  = c.text.count("⟨MATH_DISPLAY⟩")
            closes = c.text.count("⟨/MATH_DISPLAY⟩")
            assert opens == closes, (
                f"Split inside math display block: {opens} opens vs {closes} closes"
            )

    def test_thin_chunks_filtered(self):
        from ingestion.processing.normaliser import Normaliser
        from ingestion.processing.chunker    import Chunker, Strategy
        text   = "## Short\n\nFew words.\n\n## Long\n\n" + "word " * 100
        doc    = Normaliser.normalise(text, "book")
        chunks = Chunker(min_words=40).chunk(doc, Strategy.HIERARCHICAL)
        for c in chunks:
            assert not c.is_thin(40), f"Thin chunk made it through: {c.word_count} words"

    def test_overlap_continuity(self):
        from ingestion.processing.chunker import Chunker
        # Create text that will be split across two windows
        text   = "word " * 2000
        c      = Chunker(max_words=400, overlap_words=50)
        windows = c._window_split(text)
        if len(windows) >= 2:
            # Last N words of window[0] should appear at start of window[1]
            w0_tail = " ".join(windows[0].split()[-30:])
            w1_head = " ".join(windows[1].split()[:30])
            # Both should contain the same words (overlap)
            overlap_set = set(w0_tail.split()) & set(w1_head.split())
            assert len(overlap_set) > 0, "No overlap between consecutive windows"

    def test_chapter_metadata_attached(self):
        from ingestion.processing.normaliser import Normaliser
        from ingestion.processing.chunker    import Chunker, Strategy
        doc    = Normaliser.normalise(SAMPLE_MATH_TEXT, "book")
        chunks = Chunker().chunk(doc, Strategy.HIERARCHICAL)
        chaptered = [c for c in chunks if c.chapter_title]
        assert chaptered, "Some chunks should have chapter_title set"

    def test_code_chunk_detected(self):
        from ingestion.processing.normaliser import Normaliser
        from ingestion.processing.chunker    import Chunker, Strategy
        doc    = Normaliser.normalise(SAMPLE_CODE_TEXT, "book")
        chunks = Chunker().chunk(doc, Strategy.HIERARCHICAL)
        code_chunks = [c for c in chunks if c.has_code]
        assert code_chunks, "Expected at least one chunk with has_code=True"

    def test_flat_semantic_for_transcript(self):
        from ingestion.processing.normaliser import Normaliser
        from ingestion.processing.chunker    import Chunker, Strategy
        transcript = "[00:00] " + "word " * 300 + "\n\n[05:00] " + "word " * 300
        doc        = Normaliser.normalise(transcript, "youtube")
        chunks     = Chunker(max_words=200).chunk(doc, Strategy.FLAT_SEMANTIC)
        assert len(chunks) >= 2


# ─────────────────────────────────────────────────────────────────────────────
# Stage 6: Validator tests (no sandbox required)
# ─────────────────────────────────────────────────────────────────────────────

class TestValidator:

    def test_valid_problem_passes(self):
        from ingestion.generation.generator       import GeneratedProblem
        from ingestion.generation.pipeline_stages import Validator
        p      = GeneratedProblem(**MINIMAL_VALID_PROBLEM)
        result = Validator().validate(p)
        assert result.passed
        assert result.quality_score >= 0.7

    def test_syntax_error_caught(self):
        from ingestion.generation.generator       import GeneratedProblem
        from ingestion.generation.pipeline_stages import Validator
        bad = {**MINIMAL_VALID_PROBLEM, "starterCode": "def solve(\n    pass"}
        # Pydantic will accept it (no syntax check at schema level)
        # But Validator should catch it
        p      = GeneratedProblem(**{**MINIMAL_VALID_PROBLEM})
        p.starterCode = "def solve(\n    pass"  # manually corrupt
        result = Validator().validate(p)
        assert not result.passed
        assert any("syntax" in e.lower() for e in result.errors)

    def test_missing_print_statement_caught(self):
        from ingestion.generation.generator       import GeneratedProblem
        from ingestion.generation.pipeline_stages import Validator
        # testCode without print('All tests passed.')
        with pytest.raises(Exception):  # Pydantic should raise
            GeneratedProblem(**{
                **MINIMAL_VALID_PROBLEM,
                "testCode": "from solution import solve\nassert solve(1) == 1"
            })

    def test_thin_explanation_penalised(self):
        from ingestion.generation.generator       import GeneratedProblem
        from ingestion.generation.pipeline_stages import Validator
        thin = {**MINIMAL_VALID_PROBLEM,
                "explanation": (
                    "### What you are learning\nShort.\n"
                    "### The intuition\nShort.\n"
                    "### Common mistakes\nShort.\n"
                    "### Mental model check\nShort."
                )}
        p      = GeneratedProblem(**thin)
        result = Validator().validate(p)
        assert result.quality_score < 0.9  # penalised but may still pass

    def test_inline_sandbox_execution(self):
        """Test the inline (non-Docker) sandbox path."""
        from ingestion.generation.pipeline_stages import Validator
        solution = "def solve(x):\n    return x * 2\n"
        tests    = ("from solution import solve\n"
                    "assert solve(3) == 6\n"
                    "print('All tests passed.')")
        ok, msg = Validator._inline_run(solution + "\n" + tests)
        assert ok, f"Inline sandbox failed: {msg}"

    def test_inline_sandbox_failure_detected(self):
        from ingestion.generation.pipeline_stages import Validator
        solution = "def solve(x):\n    return x * 3\n"  # wrong
        tests    = ("from solution import solve\n"
                    "assert solve(3) == 6, 'wrong'\n"
                    "print('All tests passed.')")
        ok, msg = Validator._inline_run(solution + "\n" + tests)
        assert not ok
        assert "wrong" in msg or "AssertionError" in msg


# ─────────────────────────────────────────────────────────────────────────────
# Stage 8: DedupChecker tests
# ─────────────────────────────────────────────────────────────────────────────

class TestDedupChecker:

    @pytest.fixture
    def catalog_with_one(self):
        return {
            "chapters": [{"id": "la1", "title": "Vectors"}],
            "problems": [MINIMAL_VALID_PROBLEM],
        }

    def test_slug_collision_detected(self, catalog_with_one):
        from ingestion.generation.generator       import GeneratedProblem
        from ingestion.generation.pipeline_stages import DedupChecker
        checker = DedupChecker(catalog_with_one)
        p       = GeneratedProblem(**MINIMAL_VALID_PROBLEM)
        is_dup, reason = checker.is_duplicate(p)
        assert is_dup
        assert "slug collision" in reason

    def test_unique_problem_passes(self, catalog_with_one):
        from ingestion.generation.generator       import GeneratedProblem
        from ingestion.generation.pipeline_stages import DedupChecker
        checker = DedupChecker(catalog_with_one)
        different = {**MINIMAL_VALID_PROBLEM,
                     "id": "completely-different-topic-xyz",
                     "statement": "Compute the Fourier transform of a signal."}
        p         = GeneratedProblem(**different)
        is_dup, _ = checker.is_duplicate(p)
        assert not is_dup

    def test_register_updates_index(self, catalog_with_one):
        from ingestion.generation.generator       import GeneratedProblem
        from ingestion.generation.pipeline_stages import DedupChecker
        checker = DedupChecker({"chapters": [], "problems": []})
        p       = GeneratedProblem(**MINIMAL_VALID_PROBLEM)
        # Before register: not a dup
        is_dup, _ = checker.is_duplicate(p)
        assert not is_dup
        # Register it
        checker.register(p)
        # Now slug collision
        is_dup, reason = checker.is_duplicate(p)
        assert is_dup


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic schema validation tests
# ─────────────────────────────────────────────────────────────────────────────

class TestGeneratedProblemSchema:

    def test_valid_problem_parses(self):
        from ingestion.generation.generator import GeneratedProblem
        p = GeneratedProblem(**MINIMAL_VALID_PROBLEM)
        assert p.id == "test-eigenvalue-basic"
        assert p.difficulty == "medium"

    def test_uppercase_id_rejected(self):
        from ingestion.generation.generator import GeneratedProblem
        with pytest.raises(Exception):
            GeneratedProblem(**{**MINIMAL_VALID_PROBLEM, "id": "UPPERCASE-ID"})

    def test_bad_difficulty_rejected(self):
        from ingestion.generation.generator import GeneratedProblem
        with pytest.raises(Exception):
            GeneratedProblem(**{**MINIMAL_VALID_PROBLEM, "difficulty": "extreme"})

    def test_too_few_sections_rejected(self):
        from ingestion.generation.generator import GeneratedProblem
        with pytest.raises(Exception):
            GeneratedProblem(**{
                **MINIMAL_VALID_PROBLEM,
                "explanation": "### One section\nOnly one section here."
            })

    def test_too_few_hints_rejected(self):
        from ingestion.generation.generator import GeneratedProblem
        with pytest.raises(Exception):
            GeneratedProblem(**{**MINIMAL_VALID_PROBLEM, "hints": ["only one hint"]})

    def test_missing_solve_fn_rejected(self):
        from ingestion.generation.generator import GeneratedProblem
        with pytest.raises(Exception):
            GeneratedProblem(**{
                **MINIMAL_VALID_PROBLEM,
                "starterCode": "import numpy as np\n# no solve function"
            })


# ─────────────────────────────────────────────────────────────────────────────
# Source extractor unit tests (no network)
# ─────────────────────────────────────────────────────────────────────────────

class TestYouTubeExtractor:

    def test_vtt_timestamp_parsing(self):
        """Test that timestamp paragraphs are generated correctly."""
        from ingestion.sources.extractors import YouTubeExtractor

        segments = [
            {"start":  0.0, "end":  5.0, "text": "Welcome to the lecture."},
            {"start":  5.0, "end": 10.0, "text": "Today we cover eigenvalues."},
            {"start": 200.0, "end": 205.0, "text": "Now the key theorem."},
        ]
        text = YouTubeExtractor._format_transcript("Test Lecture", segments)
        assert "[00:00]" in text
        assert "[03:20]" in text or "[03:2" in text  # 200s = 3m20s
        assert "Welcome to the lecture." in text


class TestWebExtractor:

    def test_title_extraction(self):
        from ingestion.sources.extractors import WebExtractor
        text  = "# My Article Title\n\nSome content."
        title = WebExtractor._extract_title("https://example.com/post", text)
        assert title == "My Article Title"

    def test_title_fallback_from_url(self):
        from ingestion.sources.extractors import WebExtractor
        title = WebExtractor._extract_title(
            "https://example.com/understanding-transformers", ""
        )
        assert "transformers" in title.lower()


class TestGitHubExtractor:

    def test_notebook_extraction(self, tmp_path):
        from ingestion.sources.extractors import GitHubExtractor
        nb = {
            "cells": [
                {"cell_type": "markdown", "source": ["# Introduction\n", "Linear algebra."]},
                {"cell_type": "code",     "source": ["import numpy as np\na = np.eye(3)"],
                 "outputs": [{"output_type": "stream", "text": ["[[1,0,0]]\n"]}]},
            ]
        }
        nb_path = tmp_path / "lecture.ipynb"
        nb_path.write_text(json.dumps(nb))
        text = GitHubExtractor._extract_notebook(nb_path)
        assert "Introduction" in text
        assert "import numpy" in text
        assert "[[1,0,0]]" in text  # output included


# ─────────────────────────────────────────────────────────────────────────────
# Slow tests — require Docker
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.slow
class TestValidatorSandbox:

    def test_sandbox_correct_code_passes(self):
        from ingestion.generation.generator       import GeneratedProblem
        from ingestion.generation.pipeline_stages import Validator
        p      = GeneratedProblem(**MINIMAL_VALID_PROBLEM)
        result = Validator().validate(p)
        assert result.passed, f"Expected pass, errors: {result.errors}"

    def test_sandbox_wrong_code_fails(self):
        from ingestion.generation.generator       import GeneratedProblem
        from ingestion.generation.pipeline_stages import Validator
        wrong = {**MINIMAL_VALID_PROBLEM,
                 "solutionCode": "import numpy as np\ndef solve(A):\n    return np.zeros(2)"}
        p      = GeneratedProblem(**wrong)
        result = Validator().validate(p)
        assert not result.passed


# ─────────────────────────────────────────────────────────────────────────────
# pytest config
# ─────────────────────────────────────────────────────────────────────────────

def pytest_configure(config):
    config.addinivalue_line("markers",
        "slow: requires Docker sandbox")
    config.addinivalue_line("markers",
        "e2e: requires real API key in environment")
