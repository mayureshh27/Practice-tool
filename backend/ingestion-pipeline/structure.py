"""
ingestion/processing/structure.py
===================================
Book-specific structure detection.

For deep technical and maths books the hierarchy is:
  Book → Chapter → Section/Topic → Subsection → Example/Exercise/Proof

This module detects that hierarchy from normalised text and produces
a StructuredBook object that the pipeline uses to generate problems
with correct chapter metadata and proper difficulty calibration.

The key insight: a Chapter is not the same as a chunk.
A chapter might be 8 000 words — way too large for a single LLM call.
But it carries important metadata (title, number, prerequisites)
that every chunk from that chapter should inherit.

We detect exercises and worked examples explicitly because:
  - Exercises in the book text → highest priority for problem generation
    (the author already designed an exercise, we adapt it)
  - Worked examples → good starter code and solution code templates
  - Theorems/Lemmas → generate "prove this" or "apply this" problems
  - Definitions → generate "implement from definition" problems
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field


# ─────────────────────────────────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Exercise:
    """An exercise extracted verbatim from the book."""
    number:   str           # "3.2" or "Exercise 12" or "Problem 4"
    text:     str           # full exercise statement
    hint:     str | None    # if the book provides a hint
    solution: str | None    # if the book provides a solution
    tags:     list[str] = field(default_factory=list)

@dataclass
class Example:
    """A worked example from the book."""
    number: str
    title:  str
    text:   str             # full example text including solution steps

@dataclass
class Theorem:
    kind:   str             # Theorem | Lemma | Corollary | Proposition
    number: str
    text:   str
    proof:  str | None

@dataclass
class Topic:
    """A section or subsection within a chapter."""
    title:     str
    number:    str | None   # "3.2" or None for unnumbered sections
    level:     int          # 1=section, 2=subsection
    text:      str          # full text of this topic
    theorems:  list[Theorem] = field(default_factory=list)
    examples:  list[Example] = field(default_factory=list)
    exercises: list[Exercise]= field(default_factory=list)

@dataclass
class Chapter:
    """A chapter of a book."""
    title:      str
    number:     str | None  # "3" or "III"
    text:       str         # full chapter text (may be large)
    topics:     list[Topic] = field(default_factory=list)
    exercises:  list[Exercise] = field(default_factory=list)  # end-of-chapter
    difficulty_hint: str = "medium"    # inferred from chapter position

@dataclass
class StructuredBook:
    title:      str
    chapters:   list[Chapter] = field(default_factory=list)
    metadata:   dict          = field(default_factory=dict)

    @property
    def total_exercises(self) -> int:
        total = sum(len(c.exercises) for c in self.chapters)
        total += sum(len(t.exercises) for c in self.chapters
                     for t in c.topics)
        return total

    @property
    def total_theorems(self) -> int:
        return sum(len(t.theorems) for c in self.chapters
                   for t in c.topics)


# ─────────────────────────────────────────────────────────────────────────────
# Patterns
# ─────────────────────────────────────────────────────────────────────────────

# Chapter heading patterns seen in maths books
_CHAPTER_PATTERNS = [
    re.compile(r'^#\s+Chapter\s+(\d+|[IVXLC]+)[.:]\s+(.+)$', re.MULTILINE | re.IGNORECASE),
    re.compile(r'^#\s+(\d+)\s+(.+)$', re.MULTILINE),           # "# 3 Linear Algebra"
    re.compile(r'^CHAPTER\s+(\d+|[IVXLC]+)[:\s]+(.+)$', re.MULTILINE | re.IGNORECASE),
]

# Section heading patterns
_SECTION_PATTERNS = [
    re.compile(r'^##\s+(\d+\.\d+)\s+(.+)$', re.MULTILINE),     # "## 3.2 Eigenvalues"
    re.compile(r'^##\s+(.+)$', re.MULTILINE),
]

# Exercise block patterns
_EXERCISE_PATTERNS = [
    re.compile(
        r'(?:Exercise|Problem|Exercises?)\s*(\d+[\.\d]*)[.:]\s*(.*?)(?=Exercise|Problem|\Z)',
        re.DOTALL | re.IGNORECASE
    ),
    # Numbered list of exercises at chapter end
    re.compile(
        r'^\s*(\d+)\.\s+(.*?)(?=^\s*\d+\.|\Z)',
        re.MULTILINE | re.DOTALL
    ),
]

# Worked example patterns
_EXAMPLE_PATTERNS = [
    re.compile(
        r'(?:Example|Worked\s+Example)\s*(\d+[\.\d]*)[.:]\s*(.*?)(?=Example|Theorem|Lemma|Exercise|\Z)',
        re.DOTALL | re.IGNORECASE
    ),
]

# Theorem/Lemma patterns
_THEOREM_PATTERN = re.compile(
    r'(Theorem|Lemma|Corollary|Proposition)\s+(\d+[\.\d]*)[.:]\s*(.*?)'
    r'(?=Theorem|Lemma|Corollary|Proposition|Proof|Exercise|Example|\Z)',
    re.DOTALL | re.IGNORECASE
)

# Proof pattern
_PROOF_PATTERN = re.compile(
    r'Proof[.:]\s*(.*?)(?=□|∎|QED|\n\n(?=[A-Z])|\Z)',
    re.DOTALL | re.IGNORECASE
)

# Hint patterns (common in textbook exercises)
_HINT_PATTERN = re.compile(
    r'\(Hint[s]?[.:]?\s*(.*?)\)',
    re.DOTALL | re.IGNORECASE
)


# ─────────────────────────────────────────────────────────────────────────────
# Structure detector
# ─────────────────────────────────────────────────────────────────────────────

class BookStructureDetector:
    """
    Detects the chapter/topic/exercise hierarchy in a normalised book text.

    Usage:
        from ingestion.processing.normaliser import Normaliser
        from ingestion.processing.structure import BookStructureDetector

        doc = Normaliser.normalise(raw_text, source_type="book")
        book = BookStructureDetector.detect(doc.text, title="Strang LA")
    """

    @classmethod
    def detect(cls, text: str, title: str = "Unknown Book") -> StructuredBook:
        book = StructuredBook(title=title)

        # Try to split into chapters
        chapters_raw = cls._split_chapters(text)
        if not chapters_raw:
            # No chapter structure found — treat entire text as one chapter
            chapters_raw = [("1", "Content", text)]

        # Infer difficulty: early chapters easy, later chapters harder
        n = max(len(chapters_raw), 1)
        for i, (num, ch_title, ch_text) in enumerate(chapters_raw):
            diff = ("easy"   if i < n * 0.33 else
                    "medium" if i < n * 0.66 else
                    "hard")
            chapter = cls._parse_chapter(num, ch_title, ch_text, diff)
            book.chapters.append(chapter)

        return book

    @classmethod
    def _split_chapters(cls, text: str) -> list[tuple[str, str, str]]:
        """
        Split text at chapter boundaries.
        Returns list of (chapter_number, chapter_title, chapter_text).
        """
        results = []

        for pat in _CHAPTER_PATTERNS:
            matches = list(pat.finditer(text))
            if len(matches) >= 2:
                for j, m in enumerate(matches):
                    num   = m.group(1)
                    title = m.group(2).strip()
                    start = m.end()
                    end   = matches[j + 1].start() if j + 1 < len(matches) else len(text)
                    results.append((num, title, text[start:end].strip()))
                return results

        return results

    @classmethod
    def _parse_chapter(cls, num: str, title: str,
                       text: str, difficulty: str) -> Chapter:
        chapter = Chapter(
            title          = title,
            number         = num,
            text           = text,
            difficulty_hint= difficulty,
        )

        # Extract topics (sections)
        topics_raw = cls._split_topics(text)
        for t_num, t_title, t_text, t_level in topics_raw:
            topic = cls._parse_topic(t_num, t_title, t_text, t_level)
            chapter.topics.append(topic)

        # End-of-chapter exercises (common in maths books)
        # Usually after "Exercises" heading near chapter end
        ex_section = cls._find_exercise_section(text)
        if ex_section:
            chapter.exercises = cls._extract_exercises(ex_section)

        return chapter

    @classmethod
    def _split_topics(cls, text: str) -> list[tuple[str | None, str, str, int]]:
        """
        Split chapter text into (number, title, text, level) tuples.
        Level 1 = section, Level 2 = subsection.
        """
        results = []
        for pat in _SECTION_PATTERNS:
            matches = list(pat.finditer(text))
            if len(matches) >= 2:
                for j, m in enumerate(matches):
                    if m.lastindex and m.lastindex >= 2:
                        num   = m.group(1)
                        title = m.group(2).strip()
                        # Detect level by counting dots in number
                        level = num.count(".") + 1 if num and "." in num else 1
                    else:
                        num   = None
                        title = m.group(1).strip()
                        level = 1
                    start = m.end()
                    end   = matches[j + 1].start() if j + 1 < len(matches) else len(text)
                    results.append((num, title, text[start:end].strip(), level))
                return results

        # No section headings — treat as single topic
        return [(None, "Content", text, 1)]

    @classmethod
    def _parse_topic(cls, num: str | None, title: str,
                     text: str, level: int) -> Topic:
        topic = Topic(
            title    = title,
            number   = num,
            level    = level,
            text     = text,
        )
        topic.theorems  = cls._extract_theorems(text)
        topic.examples  = cls._extract_examples(text)
        topic.exercises = cls._extract_exercises(text)
        return topic

    @classmethod
    def _extract_exercises(cls, text: str) -> list[Exercise]:
        exercises = []
        for pat in _EXERCISE_PATTERNS:
            for m in pat.finditer(text):
                raw  = m.group(2).strip() if m.lastindex >= 2 else m.group(0)
                if len(raw.split()) < 5:
                    continue
                # Extract hint if present
                hint_m = _HINT_PATTERN.search(raw)
                hint   = hint_m.group(1).strip() if hint_m else None
                clean  = _HINT_PATTERN.sub("", raw).strip()
                exercises.append(Exercise(
                    number = m.group(1),
                    text   = clean[:2000],
                    hint   = hint,
                    solution = None,  # rarely in the text body
                ))
        return exercises[:30]  # cap per section

    @classmethod
    def _extract_examples(cls, text: str) -> list[Example]:
        examples = []
        for m in _EXAMPLE_PATTERNS[0].finditer(text):
            body = m.group(2).strip()
            if len(body.split()) < 20:
                continue
            # Title is first sentence
            first_sent = re.split(r'[.\n]', body)[0][:80]
            examples.append(Example(
                number = m.group(1),
                title  = first_sent,
                text   = body[:3000],
            ))
        return examples[:20]

    @classmethod
    def _extract_theorems(cls, text: str) -> list[Theorem]:
        theorems = []
        for m in _THEOREM_PATTERN.finditer(text):
            kind = m.group(1)
            num  = m.group(2)
            body = m.group(3).strip()
            # Look for proof immediately following
            proof_m = _PROOF_PATTERN.search(text[m.end():m.end() + 3000])
            proof   = proof_m.group(1).strip()[:1500] if proof_m else None
            theorems.append(Theorem(
                kind=kind, number=num,
                text=body[:2000], proof=proof
            ))
        return theorems[:15]

    @classmethod
    def _find_exercise_section(cls, text: str) -> str | None:
        """Find the end-of-chapter exercises block."""
        m = re.search(
            r'(?:^|\n)#+\s+Exercises?\s*\n(.*?)(?=\n#+\s|\Z)',
            text, re.DOTALL | re.IGNORECASE
        )
        if m:
            return m.group(1).strip()
        # Fallback: last 25% of chapter often contains exercises
        cutoff = int(len(text) * 0.75)
        tail   = text[cutoff:]
        if re.search(r'Exercise|Problem', tail, re.IGNORECASE):
            return tail
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Chunk enrichment: attach structure metadata to chunks
# ─────────────────────────────────────────────────────────────────────────────

def enrich_chunks_with_structure(
    chunks: list, book: StructuredBook
) -> list:
    """
    Given chunks produced by the Chunker and a StructuredBook,
    attach chapter/topic metadata to each chunk.

    Matching is by text overlap — find which chapter text contains
    the chunk text. Not perfect but robust for 90% of cases.
    """
    # Build lookup: chapter text fragments → chapter metadata
    ch_map = []
    for ch in book.chapters:
        ch_map.append((ch.number, ch.title, ch.difficulty_hint, ch.text))

    enriched = []
    for chunk in chunks:
        best_chapter = None
        best_overlap = 0
        for ch_num, ch_title, diff, ch_text in ch_map:
            # Count shared words as proxy for overlap
            chunk_words = set(chunk.text.lower().split())
            ch_words    = set(ch_text.lower().split())
            overlap     = len(chunk_words & ch_words)
            if overlap > best_overlap:
                best_overlap = overlap
                best_chapter = (ch_num, ch_title, diff)

        if best_chapter:
            chunk.metadata["chapter_num"]   = best_chapter[0]
            chunk.metadata["chapter_title"] = best_chapter[1]
            chunk.metadata["difficulty"]    = best_chapter[2]
            if not chunk.chapter_title:
                chunk.chapter_title = best_chapter[1]

        enriched.append(chunk)

    return enriched
