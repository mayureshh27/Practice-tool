"""
ingestion/processing/chunker.py
================================
Stage 2: NormalisedDoc → list[Chunk]

The chunker must respect mathematical and pedagogical structure:

- Never split inside a MATH_DISPLAY block (a proof mid-equation is meaningless)
- Never split inside a CODE_BLOCK
- Never split inside a THEOREM / EXERCISE / DEFINITION block
- Prefer splitting at heading boundaries
- Prefer splitting at double newlines over single newlines
- Maintain overlap: last N words of previous chunk prepended to next
  (so a definition at the end of chunk N is still visible to chunk N+1)

Three chunking strategies, selected per source type:

  HIERARCHICAL  — book PDFs with chapter/section structure
                  Produces: chapter-level chunks + section-level chunks
                  The section chunks are what go to LLM generation.
                  Chapter chunks are indexed for RAG context.

  FLAT_SEMANTIC — YouTube transcripts, web articles
                  No reliable heading structure.
                  Split on semantic similarity shifts (embedding diff)
                  with a fallback to word count.

  HYBRID        — GitHub repos, documentation
                  File-level chunks for code, section-level for docs.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from enum import Enum
from .normaliser import NormalisedDoc, TAG_MATH_DISPLAY, TAG_CODE_BLOCK
from .normaliser import TAG_THEOREM, TAG_EXERCISE, TAG_DEFINITION


# ─────────────────────────────────────────────────────────────────────────────
# Chunk dataclass — what the LLM generator receives
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Chunk:
    text:          str
    chapter_title: str | None     = None
    section_title: str | None     = None
    chapter_num:   str | None     = None    # "3" or "3.2" from numbered heading
    word_count:    int            = 0
    has_math:      bool           = False
    has_code:      bool           = False
    has_theorem:   bool           = False
    has_exercise:  bool           = False
    source_type:   str            = "unknown"
    source_url:    str | None     = None
    page_hint:     str | None     = None    # "p.42" if PDF page info available
    metadata:      dict           = field(default_factory=dict)

    def is_thin(self, min_words: int = 40) -> bool:
        return self.word_count < min_words

    def is_primarily_code(self) -> bool:
        code_chars = len(re.findall(r'⟨CODE_BLOCK', self.text))
        return code_chars >= 2 and self.word_count < 200


class Strategy(str, Enum):
    HIERARCHICAL  = "hierarchical"
    FLAT_SEMANTIC = "flat_semantic"
    HYBRID        = "hybrid"


# ─────────────────────────────────────────────────────────────────────────────
# Protected region detection
# ─────────────────────────────────────────────────────────────────────────────

# Any open tag that has a corresponding close tag — do not split inside
_PROTECTED_OPEN = [
    TAG_MATH_DISPLAY[0],
    "⟨CODE_BLOCK",       # prefix match because lang= varies
    TAG_THEOREM[0],
    TAG_EXERCISE[0],
    TAG_DEFINITION[0],
]
_PROTECTED_CLOSE = [
    TAG_MATH_DISPLAY[1],
    TAG_CODE_BLOCK[1],
    TAG_THEOREM[1],
    TAG_EXERCISE[1],
    TAG_DEFINITION[1],
]


def _is_safe_split(lines: list[str], idx: int) -> bool:
    """Return True if we can split after line idx without breaking a protected block."""
    depth = 0
    for line in lines[:idx + 1]:
        for tag in _PROTECTED_OPEN:
            depth += line.count(tag)
        for tag in _PROTECTED_CLOSE:
            depth -= line.count(tag)
    return depth == 0


# ─────────────────────────────────────────────────────────────────────────────
# Heading parser — extracts hierarchy from normalised text
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Section:
    level:   int          # 1 = chapter, 2 = section
    title:   str
    num:     str | None   # "3.2" if numbered
    lines:   list[str]    = field(default_factory=list)

_HEADING_LINE = re.compile(r'^(#{1,2})\s+(.+)$')
_NUM_PREFIX   = re.compile(r'^(\d+(?:\.\d+)*)\s+')


def _parse_sections(text: str) -> list[Section]:
    """Split normalised text into Section objects based on heading lines."""
    lines    = text.splitlines(keepends=True)
    sections: list[Section] = []
    current:  Section | None = None

    for line in lines:
        m = _HEADING_LINE.match(line.rstrip())
        if m:
            if current is not None:
                sections.append(current)
            level = len(m.group(1))
            raw_title = m.group(2).strip()
            n = _NUM_PREFIX.match(raw_title)
            num   = n.group(1) if n else None
            title = raw_title[n.end():].strip() if n else raw_title
            current = Section(level=level, title=title, num=num)
        else:
            if current is None:
                current = Section(level=1, title="Preamble", num=None)
            current.lines.append(line)

    if current is not None:
        sections.append(current)

    return sections


# ─────────────────────────────────────────────────────────────────────────────
# Main chunker
# ─────────────────────────────────────────────────────────────────────────────

class Chunker:
    def __init__(self, max_words: int = 900, min_words: int = 40,
                 overlap_words: int = 60):
        self.max_words     = max_words
        self.min_words     = min_words
        self.overlap_words = overlap_words

    def chunk(self, doc: NormalisedDoc,
              strategy: Strategy = Strategy.HIERARCHICAL) -> list[Chunk]:
        if strategy == Strategy.HIERARCHICAL:
            return self._hierarchical(doc)
        elif strategy == Strategy.FLAT_SEMANTIC:
            return self._flat_semantic(doc)
        else:
            return self._hybrid(doc)

    # ── Strategy: HIERARCHICAL ────────────────────────────────────────────────

    def _hierarchical(self, doc: NormalisedDoc) -> list[Chunk]:
        """
        For books and structured documents.
        Each section becomes one or more chunks.
        Chapter boundary is tracked so every chunk knows which chapter it belongs to.
        """
        sections = _parse_sections(doc.text)
        chunks: list[Chunk] = []
        current_chapter: str | None = None
        current_chapter_num: str | None = None

        for sec in sections:
            if sec.level == 1:
                current_chapter     = sec.title
                current_chapter_num = sec.num

            body = "".join(sec.lines).strip()
            if not body:
                continue

            # Split body into word-count windows, respecting protected blocks
            windows = self._window_split(body)
            for w_text in windows:
                wc = len(w_text.split())
                if wc < self.min_words:
                    continue
                chunks.append(Chunk(
                    text           = w_text,
                    chapter_title  = current_chapter,
                    section_title  = sec.title,
                    chapter_num    = current_chapter_num or sec.num,
                    word_count     = wc,
                    has_math       = TAG_MATH_DISPLAY[0] in w_text or
                                     "⟨MATH_INLINE⟩" in w_text,
                    has_code       = "⟨CODE_BLOCK" in w_text,
                    has_theorem    = TAG_THEOREM[0] in w_text,
                    has_exercise   = TAG_EXERCISE[0] in w_text,
                    source_type    = doc.source_type,
                    metadata       = {**doc.metadata,
                                      "section": sec.title,
                                      "chapter": current_chapter},
                ))
        return chunks

    # ── Strategy: FLAT_SEMANTIC ───────────────────────────────────────────────

    def _flat_semantic(self, doc: NormalisedDoc) -> list[Chunk]:
        """
        For transcripts and articles with no reliable heading structure.
        Split on paragraph boundaries first, then merge until word budget.
        """
        paragraphs = re.split(r'\n{2,}', doc.text)
        windows    = self._merge_paragraphs(paragraphs)
        chunks     = []
        for w in windows:
            wc = len(w.split())
            if wc < self.min_words:
                continue
            chunks.append(Chunk(
                text        = w,
                word_count  = wc,
                has_math    = TAG_MATH_DISPLAY[0] in w,
                has_code    = "⟨CODE_BLOCK" in w,
                source_type = doc.source_type,
                metadata    = doc.metadata,
            ))
        return chunks

    # ── Strategy: HYBRID ─────────────────────────────────────────────────────

    def _hybrid(self, doc: NormalisedDoc) -> list[Chunk]:
        """
        For GitHub repos and docs.
        Files with code → flat semantic on the code + docstrings.
        Markdown files → hierarchical.
        """
        # Detect if this is primarily code
        code_density = doc.text.count("⟨CODE_BLOCK") / max(len(doc.text) / 1000, 1)
        if code_density > 0.5:
            return self._flat_semantic(doc)
        return self._hierarchical(doc)

    # ── Window split ──────────────────────────────────────────────────────────

    def _window_split(self, text: str) -> list[str]:
        """
        Split text into max_words windows.
        Respects protected blocks — will not split inside them.
        Adds overlap_words of previous chunk to maintain context.
        """
        lines    = text.splitlines(keepends=True)
        windows: list[str] = []
        current: list[str] = []
        c_words  = 0
        overlap_tail: list[str] = []

        for i, line in enumerate(lines):
            line_words = len(line.split())
            if c_words + line_words > self.max_words:
                # Only split if safe (not inside protected block)
                if _is_safe_split(lines, i - 1) and current:
                    window_text = "".join(overlap_tail + current)
                    windows.append(window_text.strip())
                    # Compute overlap tail: last overlap_words from current
                    flat = " ".join("".join(current).split())
                    tail_words = flat.split()[-self.overlap_words:]
                    overlap_tail = [" ".join(tail_words) + "\n"]
                    current = []
                    c_words = len(overlap_tail[0].split())
            current.append(line)
            c_words += line_words

        if current:
            windows.append("".join(overlap_tail + current).strip())

        return windows

    def _merge_paragraphs(self, paragraphs: list[str]) -> list[str]:
        """Merge short paragraphs into windows up to max_words."""
        windows: list[str] = []
        current: list[str] = []
        c_words  = 0

        for para in paragraphs:
            pw = len(para.split())
            if c_words + pw > self.max_words and current:
                windows.append("\n\n".join(current))
                current = []
                c_words = 0
            current.append(para)
            c_words += pw

        if current:
            windows.append("\n\n".join(current))

        return windows
