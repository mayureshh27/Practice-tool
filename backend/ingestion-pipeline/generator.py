"""
ingestion/generation/generator.py
===================================
Stage 3: Chunk → GeneratedProblem

The generator is source-type aware.
A book chapter chunk needs a different prompt than a YouTube lecture chunk
or a GitHub repo module — the structural hints differ, the exercise format
differs, and the expected depth differs.

All generation goes through Instructor + Pydantic for guaranteed schema.
Temperature is always 0 for structural fields, can vary for explanations.

GENERATION_PROMPT design principles:
  - State the source type explicitly so the model knows expected depth
  - Give concrete format requirements (not just "write tests")
  - Provide negative examples for common failure modes
  - Require minimum section counts in explanation (for outline nav)
  - Demand that testCode is self-contained and runnable

Math-heavy chunks get additional prompt augmentation:
  - "Preserve all LaTeX notation exactly"
  - "The explanation must include at least one worked example"
  - "Hints must never name the specific formula — guide to it"
"""

from __future__ import annotations

import re
from dataclasses import field
from typing import Self

import instructor
import litellm
from pydantic import BaseModel, field_validator, model_validator

from .chunker import Chunk

# ─────────────────────────────────────────────────────────────────────────────
# Output schema — Pydantic enforced via Instructor
# ─────────────────────────────────────────────────────────────────────────────

class GeneratedProblem(BaseModel):
    id:           str
    number:       int
    title:        str
    chapter:      str
    difficulty:   str
    tags:         list[str]
    exerciseMode: str
    verifier:     str
    statement:    str
    problemText:  str
    explanation:  str
    howItWorks:   str
    syntax:       str
    solve:        str
    hints:        list[str]
    starterCode:  str
    solutionCode: str
    testCode:     str
    examples:     list[dict[str, str]]
    # Extra fields for math-heavy content
    prerequisites: list[str]  = field(default_factory=list)
    mathConcepts:  list[str]  = field(default_factory=list)
    sourceRef:     str        = ""   # "Strang §3.2" or "[14:32]" for video

    @field_validator("id")
    def id_kebab(cls, v: str) -> str:
        assert re.match(r"^[a-z0-9][a-z0-9-]*$", v), \
            f"id must be lowercase kebab-case, got {v!r}"
        return v

    @field_validator("difficulty")
    def diff_valid(cls, v: str) -> str:
        assert v in {"easy", "medium", "hard"}, \
            f"difficulty must be easy|medium|hard, got {v!r}"
        return v

    @field_validator("exerciseMode")
    def mode_valid(cls, v: str) -> str:
        assert v in {"judge", "project"}, \
            f"exerciseMode must be judge|project, got {v!r}"
        return v

    @field_validator("explanation")
    def needs_sections(cls, v: str) -> str:
        count = len(re.findall(r'^#{2,3}\s+', v, re.MULTILINE))
        assert count >= 4, \
            f"explanation needs ≥4 ### sections for outline nav, found {count}"
        return v

    @field_validator("hints")
    def needs_hints(cls, v: list) -> list:
        assert len(v) >= 3, f"need ≥3 hints, got {len(v)}"
        return v

    @field_validator("testCode")
    def test_runnable(cls, v: str) -> str:
        assert "print('All tests passed.')" in v or \
               'print("All tests passed.")' in v, \
            "testCode must end with print('All tests passed.')"
        return v

    @model_validator(mode="after")
    def starter_has_solve(self) -> Self:
        assert "def solve" in self.starterCode, \
            "starterCode must contain a def solve() function"
        return self


# ─────────────────────────────────────────────────────────────────────────────
# Generation prompts — one per source type
# ─────────────────────────────────────────────────────────────────────────────

_BASE_SCHEMA_RULES = """
SCHEMA RULES (every field mandatory unless marked optional):
  id           → unique kebab-case slug, all lowercase, hyphens only
  difficulty   → exactly one of: easy | medium | hard
  exerciseMode → "judge" if a def solve() can be auto-tested, else "project"
  verifier     → always "local-tests"
  starterCode  → Python with numpy/scipy available, must contain def solve(...)
  solutionCode → clean, correct Python implementation
  testCode     → Python assertions only, must end with:
                   print('All tests passed.')
                 Import from solution module: from solution import solve
                 Test at least 3 cases including an edge case
  explanation  → Markdown with ≥4 ### sections. Must include:
                   ### What you are learning
                   ### The intuition
                   ### Common mistakes  ← most important for maths
                   ### Mental model check
  hints        → exactly 3 items, each Socratic (question or concept pointer,
                 NEVER the answer or the formula name)
  prerequisites → list of concept slugs that must be mastered first
  mathConcepts  → list of mathematical objects used (e.g. "dot_product",
                  "eigenvalue", "conditional_probability")

QUALITY REQUIREMENTS:
  - explanation must build genuine intuition, not restate the definition
  - The "Common mistakes" section is mandatory for any maths problem
  - testCode must test the semantics, not just that the function runs
  - hints must never name the specific function or operation that solves it
  - If the chunk contains a theorem, the problem must test understanding
    of the theorem, not just its application
"""

BOOK_PROMPT = """
You are generating a practice problem from a technical/mathematical textbook excerpt.
Target learner: engineering student at upper-undergraduate / early-graduate level.
Chapter: {chapter}
Problem number: {number}

Source context flags:
  has_math:      {has_math}
  has_theorem:   {has_theorem}
  has_exercise:  {has_exercise}
  section:       {section}
  source_ref:    {source_ref}

TEXTBOOK EXCERPT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chunk}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MATH RULES (only if has_math=True):
  - Preserve ALL LaTeX notation exactly in explanation and syntax fields
  - explanation must include at least one fully worked numerical example
  - solutionCode must verify the result numerically with np.isclose()
  - The "Mental model check" section must give a geometric or physical
    interpretation, not just the algebraic formula

THEOREM RULES (only if has_theorem=True):
  - The problem must test UNDERSTANDING of the theorem, not just application
  - Include at least one test case that would fail if the student
    only memorised the formula without understanding the conditions

{base_schema_rules}

Return JSON only. No markdown fences. No preamble.
"""

GITHUB_PROMPT = """
You are generating a practice problem from technical documentation or source code.
Target learner: developer learning this library/framework.
Chapter: {chapter}
Problem number: {number}

Source context flags:
  has_code: {has_code}
  repo:     {repo}
  file:     {section}

DOCUMENTATION / CODE EXCERPT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chunk}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOCUMENTATION RULES:
  - Problem must require actually using the library API, not describing it
  - testCode must import the real library and test real behavior
  - exerciseMode should be "project" for open-ended integration tasks,
    "judge" only if there is one deterministic correct output
  - starterCode should include the import statements the student needs
  - "Common mistakes" section must list the 2-3 API misuses beginners make

{base_schema_rules}

Return JSON only. No markdown fences. No preamble.
"""

YOUTUBE_PROMPT = """
You are generating a practice problem from a technical lecture transcript.
Target learner: engineering student watching this lecture series.
Chapter: {chapter}
Problem number: {number}

Source context flags:
  video_title:    {video_title}
  timestamp_hint: {timestamp_hint}
  has_math:       {has_math}

LECTURE TRANSCRIPT SEGMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chunk}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LECTURE RULES:
  - Transcripts are informal — extract the core technical idea, ignore filler
  - The problem should test the concept the lecturer is explaining,
    not repeat the exact phrasing from the transcript
  - sourceRef field: use "[MM:SS]" timestamp format
  - If the lecturer gives an example, use a different but isomorphic example
    in the problem (so students cannot just copy the lecture example)
  - "What you are learning" section must connect to the broader lecture series

{base_schema_rules}

Return JSON only. No markdown fences. No preamble.
"""

WEB_PROMPT = """
You are generating a practice problem from a technical blog post or article.
Target learner: practitioner reading this article.
Chapter: {chapter}
Problem number: {number}

Source context flags:
  article_title: {article_title}
  has_math:      {has_math}
  has_code:      {has_code}

ARTICLE EXCERPT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chunk}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ARTICLE RULES:
  - Articles often explain concepts with narrative — extract the testable idea
  - If the article shows a code snippet, the problem should extend or adapt it,
    not copy it
  - exerciseMode: use "judge" only if the concept has a deterministic answer
  - "Common mistakes" section should reference the misconceptions the article
    itself warns about (authors usually know where readers go wrong)

{base_schema_rules}

Return JSON only. No markdown fences. No preamble.
"""

PROMPT_MAP = {
    "book":    BOOK_PROMPT,
    "github":  GITHUB_PROMPT,
    "youtube": YOUTUBE_PROMPT,
    "web":     WEB_PROMPT,
}


# ─────────────────────────────────────────────────────────────────────────────
# Generator
# ─────────────────────────────────────────────────────────────────────────────

class Generator:
    """
    Wraps Instructor + LiteLLM for model-agnostic structured generation.

    model_key examples:
      "claude-sonnet-4-20250514"  — best quality for maths
      "claude-haiku-4-5-20251001" — fast, for bulk generation of easy problems
      "gpt-4o"                    — alternative
      "gemini/gemini-1.5-flash"   — long context, cheap
      "ollama/llama3.1"           — local, no API cost
    """

    def __init__(self, model_key: str, api_key: str | None = None,
                 base_url: str | None = None):
        self.model    = model_key
        self.api_key  = api_key
        self.base_url = base_url
        # Patch LiteLLM with Instructor for validated structured output
        self._client  = instructor.from_litellm(litellm.completion)

    def generate(self, chunk: Chunk, chapter_id: str,
                 problem_number: int) -> GeneratedProblem:
        """Single attempt — caller manages retries."""
        prompt = self._build_prompt(chunk, chapter_id, problem_number)
        return self._client(
            model          = self.model,
            api_key        = self.api_key,
            base_url       = self.base_url,
            response_model = GeneratedProblem,
            max_retries    = 0,   # pipeline manages retries
            temperature    = 0,   # deterministic structure
            messages       = [{"role": "user", "content": prompt}],
        )

    def _build_prompt(self, chunk: Chunk, chapter_id: str,
                      problem_number: int) -> str:
        src   = chunk.source_type
        tmpl  = PROMPT_MAP.get(src, BOOK_PROMPT)

        # Shared substitutions
        common = dict(
            chunk            = chunk.text,
            chapter          = chapter_id,
            number           = problem_number,
            has_math         = chunk.has_math,
            has_code         = chunk.has_code,
            has_theorem      = chunk.has_theorem,
            has_exercise     = chunk.has_exercise,
            section          = chunk.section_title or "",
            source_ref       = chunk.metadata.get("source_ref", ""),
            base_schema_rules= _BASE_SCHEMA_RULES,
        )

        # Source-specific substitutions
        if src == "youtube":
            common["video_title"]    = chunk.metadata.get("title", "")
            common["timestamp_hint"] = chunk.metadata.get("timestamp", "")
        elif src == "github":
            common["repo"] = chunk.metadata.get("repo", "")
        elif src == "web":
            common["article_title"] = chunk.metadata.get("title", "")

        # Fill only the keys that exist in the template
        try:
            return tmpl.format(**common)
        except KeyError as e:
            # Template has a key we did not fill — use safe fallback
            return tmpl.format_map({**common, **{str(e).strip("'"): ""}})
