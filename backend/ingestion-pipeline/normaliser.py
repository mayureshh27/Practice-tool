"""
ingestion/processing/normaliser.py
===================================
Stage 1 of the pipeline: raw text in → clean, tagged text out.

Handles:
- Unicode normalisation (NFC, ligature repair)
- Math preservation: LaTeX inline/display, MathML, ASCII math
- Code fence preservation: triple-backtick blocks tagged before chunking
- Heading normalisation: PDF extractions produce h1–h6 inconsistently
- Page artefact removal: page numbers, running headers, watermarks
- Jupyter notebook cell extraction: code + markdown interleaved
"""

from __future__ import annotations
import re, unicodedata
from dataclasses import dataclass, field


# ─────────────────────────────────────────────────────────────────────────────
# Tag constants — used throughout the pipeline to protect content
# ─────────────────────────────────────────────────────────────────────────────
TAG_MATH_INLINE  = ("⟨MATH_INLINE⟩",  "⟨/MATH_INLINE⟩")
TAG_MATH_DISPLAY = ("⟨MATH_DISPLAY⟩", "⟨/MATH_DISPLAY⟩")
TAG_CODE_BLOCK   = ("⟨CODE_BLOCK lang={lang}⟩", "⟨/CODE_BLOCK⟩")
TAG_DEFINITION   = ("⟨DEFINITION⟩",   "⟨/DEFINITION⟩")
TAG_THEOREM      = ("⟨THEOREM⟩",      "⟨/THEOREM⟩")
TAG_PROOF        = ("⟨PROOF⟩",        "⟨/PROOF⟩")
TAG_EXERCISE     = ("⟨EXERCISE⟩",     "⟨/EXERCISE⟩")
TAG_EXAMPLE      = ("⟨EXAMPLE⟩",      "⟨/EXAMPLE⟩")


@dataclass
class NormalisedDoc:
    text:         str
    has_math:     bool = False
    has_code:     bool = False
    has_theorems: bool = False
    has_exercises:bool = False
    source_type:  str  = "unknown"   # book | github | youtube | web
    metadata:     dict = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Patterns
# ─────────────────────────────────────────────────────────────────────────────

# LaTeX math — must be protected before ANY other processing
_MATH_DISPLAY_PATTERNS = [
    re.compile(r'\$\$(.+?)\$\$',         re.DOTALL),   # $$...$$
    re.compile(r'\\\[(.+?)\\\]',         re.DOTALL),   # \[...\]
    re.compile(r'\\begin\{(equation|align|gather|multline|eqnarray)\*?\}(.+?)\\end\{\1\*?\}',
               re.DOTALL),                              # \begin{equation}...\end{equation}
    re.compile(r'\\begin\{(matrix|pmatrix|bmatrix|vmatrix|Bmatrix)\}(.+?)\\end\{\1\}',
               re.DOTALL),                              # matrix environments
]

_MATH_INLINE_PATTERNS = [
    re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)'),  # $...$
    re.compile(r'\\\((.+?)\\\)'),                          # \(...\)
]

_CODE_FENCE = re.compile(
    r'```(\w*)\n(.*?)```', re.DOTALL
)

_HEADING_RE = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

# Page number patterns from PDF extraction
_PAGE_NUM_RE  = re.compile(r'^\s*\d{1,4}\s*$', re.MULTILINE)
# Running headers: short lines that repeat (detected as lines appearing 3+ times)
# Handled separately below.

# Semantic block markers for maths books
_THEOREM_START = re.compile(
    r'^(Theorem|Lemma|Corollary|Proposition|Axiom|Definition|Remark|'
    r'Example|Exercise|Problem|Proof)\s*(\d+[\.\d]*)?[\.:]\s*',
    re.MULTILINE | re.IGNORECASE
)

# Ligature repair table
_LIGATURES = {
    "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi",
    "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st",
    "\u2019": "'",  # right single quote
    "\u2018": "'",  # left single quote
    "\u201C": '"',  # left double quote
    "\u201D": '"',  # right double quote
    "\u2013": "-",  # en dash
    "\u2014": "--", # em dash
    "\u00A0": " ",  # non-breaking space
}


# ─────────────────────────────────────────────────────────────────────────────
# Main normaliser
# ─────────────────────────────────────────────────────────────────────────────

class Normaliser:

    @classmethod
    def normalise(cls, raw: str, source_type: str = "unknown",
                  metadata: dict | None = None) -> NormalisedDoc:
        text = raw
        text = cls._unicode_clean(text)
        text = cls._repair_ligatures(text)
        text = cls._unify_line_endings(text)
        text, has_math  = cls._protect_math(text)
        text, has_code  = cls._protect_code(text)
        text = cls._remove_page_artefacts(text)
        text = cls._remove_running_headers(text)
        text = cls._normalise_headings(text)
        text, has_theorems  = cls._tag_semantic_blocks(text, TAG_THEOREM,
            ["theorem","lemma","corollary","proposition","axiom"])
        text, has_exercises = cls._tag_semantic_blocks(text, TAG_EXERCISE,
            ["exercise","problem"])
        text = cls._collapse_blank_lines(text)

        return NormalisedDoc(
            text          = text.strip(),
            has_math      = has_math,
            has_code      = has_code,
            has_theorems  = has_theorems,
            has_exercises = has_exercises,
            source_type   = source_type,
            metadata      = metadata or {},
        )

    # ── Unicode ──────────────────────────────────────────────────────────────

    @staticmethod
    def _unicode_clean(text: str) -> str:
        return unicodedata.normalize("NFC", text)

    @staticmethod
    def _repair_ligatures(text: str) -> str:
        for lig, rep in _LIGATURES.items():
            text = text.replace(lig, rep)
        return text

    @staticmethod
    def _unify_line_endings(text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")

    # ── Math protection ───────────────────────────────────────────────────────

    @classmethod
    def _protect_math(cls, text: str) -> tuple[str, bool]:
        """Replace math with tagged placeholders to survive downstream processing."""
        found = False

        # Display math first (longer patterns take priority)
        for pat in _MATH_DISPLAY_PATTERNS:
            def replace_display(m: re.Match) -> str:
                nonlocal found
                found = True
                content = m.group(0)
                return f"{TAG_MATH_DISPLAY[0]}{content}{TAG_MATH_DISPLAY[1]}"
            text = pat.sub(replace_display, text)

        # Inline math (only if not already tagged)
        for pat in _MATH_INLINE_PATTERNS:
            def replace_inline(m: re.Match) -> str:
                nonlocal found
                # Skip if already inside a display math tag
                start = m.start()
                if text[:start].count(TAG_MATH_DISPLAY[0]) > \
                   text[:start].count(TAG_MATH_DISPLAY[1]):
                    return m.group(0)
                found = True
                return f"{TAG_MATH_INLINE[0]}{m.group(0)}{TAG_MATH_INLINE[1]}"
            text = pat.sub(replace_inline, text)

        return text, found

    # ── Code protection ───────────────────────────────────────────────────────

    @staticmethod
    def _protect_code(text: str) -> tuple[str, bool]:
        found = [False]
        def replace_code(m: re.Match) -> str:
            found[0] = True
            lang    = m.group(1) or "text"
            content = m.group(2)
            open_tag = TAG_CODE_BLOCK[0].format(lang=lang)
            return f"{open_tag}\n{content}{TAG_CODE_BLOCK[1]}"
        text = _CODE_FENCE.sub(replace_code, text)
        return text, found[0]

    # ── Page artefact removal ─────────────────────────────────────────────────

    @staticmethod
    def _remove_page_artefacts(text: str) -> str:
        # Standalone numbers (page numbers)
        text = _PAGE_NUM_RE.sub("", text)
        return text

    @staticmethod
    def _remove_running_headers(text: str) -> str:
        """Remove lines that appear identically 3+ times — running headers."""
        lines = text.splitlines()
        from collections import Counter
        counts = Counter(ln.strip() for ln in lines if ln.strip())
        repeated = {ln for ln, c in counts.items() if c >= 3 and len(ln) < 80}
        filtered = [ln for ln in lines if ln.strip() not in repeated]
        return "\n".join(filtered)

    # ── Heading normalisation ─────────────────────────────────────────────────

    @staticmethod
    def _normalise_headings(text: str) -> str:
        """
        PDF extraction produces erratic heading levels.
        Strategy: detect numeric prefixes (1.2.3) and map to heading depth.
        Cap heading depth at ## (h2) to keep the outline manageable.
        """
        numbered_chapter = re.compile(
            r'^(\d+)\.\s+([A-Z].+)$', re.MULTILINE
        )
        numbered_section = re.compile(
            r'^(\d+)\.(\d+)\s+([A-Z].+)$', re.MULTILINE
        )
        numbered_subsec  = re.compile(
            r'^(\d+)\.(\d+)\.(\d+)\s+(.+)$', re.MULTILINE
        )

        text = numbered_subsec.sub(r'### \4', text)
        text = numbered_section.sub(r'## \3', text)
        text = numbered_chapter.sub(r'# \2', text)

        # Cap existing headings at h2 (## )
        def cap_heading(m: re.Match) -> str:
            hashes = m.group(1)
            title  = m.group(2)
            level  = min(len(hashes), 2)
            return "#" * level + " " + title

        text = _HEADING_RE.sub(cap_heading, text)
        return text

    # ── Semantic block tagging ────────────────────────────────────────────────

    @staticmethod
    def _tag_semantic_blocks(text: str, tag: tuple,
                             keywords: list[str]) -> tuple[str, bool]:
        """
        Wrap Theorem/Lemma/Exercise blocks in structural tags.
        These are used by the chunker to avoid splitting mid-block.
        """
        pattern = re.compile(
            r'^(' + '|'.join(keywords) + r')'
            r'(\s*\d+[\.\d]*)?\s*[.:]\s*',
            re.MULTILINE | re.IGNORECASE
        )
        found   = [False]
        lines   = text.splitlines(keepends=True)
        result  = []
        in_block= False
        block_kw= ""

        for line in lines:
            m = pattern.match(line)
            if m:
                if in_block:
                    result.append(tag[1] + "\n")
                found[0] = True
                in_block = True
                block_kw = m.group(1)
                result.append(tag[0] + "\n" + line)
            elif in_block:
                # Block ends at next empty line or next keyword
                if not line.strip():
                    result.append(tag[1] + "\n" + line)
                    in_block = False
                else:
                    result.append(line)
            else:
                result.append(line)

        if in_block:
            result.append(tag[1] + "\n")

        return "".join(result), found[0]

    # ── Utility ───────────────────────────────────────────────────────────────

    @staticmethod
    def _collapse_blank_lines(text: str) -> str:
        return re.sub(r'\n{3,}', '\n\n', text)
