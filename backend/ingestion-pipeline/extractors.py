"""
ingestion/sources/extractors.py
================================
Four source extractors — all return (raw_text, metadata_dict).

BOOK     — PDF, LaTeX, EPUB
GITHUB   — repos, library docs, notebooks
YOUTUBE  — single video or full playlist, local transcription
WEB      — articles, Substack, blogs, arXiv abstracts

Design principle: extractors do ONE thing — produce raw text + metadata.
They do not clean, chunk, or generate. The pipeline handles that.
"""

from __future__ import annotations
import json, re, subprocess, tempfile
from dataclasses import dataclass
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Return type
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RawSource:
    text:     str
    metadata: dict
    source_type: str   # book | github | youtube | web


# ─────────────────────────────────────────────────────────────────────────────
# 1. BOOK EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────

class BookExtractor:
    """
    PDF → markdown with math preservation.

    Tries Docling first (handles scanned PDFs, equations, figures).
    Falls back to pymupdf4llm (faster, better for clean PDFs).
    Falls back to pdfminer (last resort, text only).

    LaTeX .tex files are read directly — no extraction needed.
    EPUB files use ebooklib.
    """

    @classmethod
    def extract(cls, path: str, title: str = "") -> RawSource:
        p = Path(path)
        ext = p.suffix.lower()

        if ext == ".pdf":
            text = cls._from_pdf(path)
        elif ext in (".tex", ".ltx"):
            text = cls._from_latex(path)
        elif ext == ".epub":
            text = cls._from_epub(path)
        elif ext in (".md", ".rst", ".txt"):
            text = p.read_text(errors="ignore")
        else:
            raise ValueError(f"Unsupported book format: {ext}")

        return RawSource(
            text        = text,
            metadata    = {"title": title or p.stem, "path": str(p)},
            source_type = "book",
        )

    @staticmethod
    def _from_pdf(path: str) -> str:
        # Try Docling (handles equations, figures, tables, scanned)
        try:
            from docling.document_converter import DocumentConverter
            result = DocumentConverter().convert(path)
            return result.document.export_to_markdown()
        except Exception:
            pass

        # Try pymupdf4llm (fast, clean PDFs)
        try:
            import pymupdf4llm
            return pymupdf4llm.to_markdown(path)
        except Exception:
            pass

        # Fallback: pdfminer
        from pdfminer.high_level import extract_text
        return extract_text(path)

    @staticmethod
    def _from_latex(path: str) -> str:
        """
        LaTeX source is gold — math is already in LaTeX notation.
        Strip preamble and \begin{document}...\end{document} wrapper.
        Keep all math environments intact.
        """
        raw = Path(path).read_text(errors="ignore")
        # Extract body
        body_match = re.search(
            r'\\begin\{document\}(.*?)\\end\{document\}',
            raw, re.DOTALL
        )
        if body_match:
            raw = body_match.group(1)
        # Convert common LaTeX structure to markdown headings
        raw = re.sub(r'\\chapter\{(.+?)\}',  r'# \1',  raw)
        raw = re.sub(r'\\section\{(.+?)\}',  r'## \1', raw)
        raw = re.sub(r'\\subsection\{(.+?)\}', r'### \1', raw)
        # Strip LaTeX commands that add no semantic value
        raw = re.sub(r'\\(label|ref|cite|footnote|marginpar)\{[^}]*\}', '', raw)
        raw = re.sub(r'\\(textbf|textit|emph|texttt)\{([^}]*)\}', r'\2', raw)
        # Keep math environments as-is — normaliser will tag them
        return raw

    @staticmethod
    def _from_epub(path: str) -> str:
        import ebooklib
        from ebooklib import epub
        from html.parser import HTMLParser

        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.parts = []
            def handle_data(self, data):
                self.parts.append(data)

        book  = epub.read_epub(path)
        parts = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            parser = TextExtractor()
            parser.feed(item.get_content().decode("utf-8", errors="ignore"))
            parts.append("".join(parser.parts))
        return "\n\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# 2. GITHUB EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────

class GitHubExtractor:
    """
    Extracts content from a GitHub repository for ingestion.

    Three modes:
      full      — entire repo (README + all docs + all .py with docstrings)
      docs_only — only documentation files (md, rst, txt)
      code_only — only Python/JS/Go source files

    Notebook (.ipynb) handling: interleave markdown cells and code cells
    with output for richer context.

    Returns one RawSource per logical section (README + each module).
    But for pipeline simplicity, concatenates into one large doc.
    """

    INCLUDE_EXTENSIONS = {".md", ".rst", ".txt", ".py", ".ipynb",
                          ".go", ".ts", ".js", ".yaml", ".toml"}
    SKIP_DIRS          = {".git", "node_modules", "__pycache__", ".venv",
                          "venv", "dist", "build", ".eggs", "*.egg-info"}
    MAX_FILE_BYTES     = 200_000
    MAX_TOTAL_WORDS    = 50_000  # safety cap for large repos

    @classmethod
    def extract(cls, url_or_path: str, mode: str = "full",
                branch: str = "main") -> RawSource:
        if url_or_path.startswith("http"):
            path = cls._clone(url_or_path, branch)
        else:
            path = Path(url_or_path)

        files  = cls._collect_files(path, mode)
        parts  = []
        total  = 0

        # README always first
        for readme in sorted(path.glob("README*")):
            try:
                content = readme.read_text(errors="ignore")
                parts.append(f"# {readme.name}\n\n{content}")
                total += len(content.split())
            except Exception:
                pass

        for fpath in files:
            if total > cls.MAX_TOTAL_WORDS:
                break
            try:
                content = cls._extract_file(fpath)
                if len(content.split()) < 20:
                    continue
                rel = fpath.relative_to(path)
                parts.append(f"## FILE: {rel}\n\n{content}")
                total += len(content.split())
            except Exception:
                pass

        name = path.name if path.exists() else url_or_path.split("/")[-1]
        return RawSource(
            text        = "\n\n---\n\n".join(parts),
            metadata    = {"repo": name, "url": url_or_path, "mode": mode},
            source_type = "github",
        )

    @classmethod
    def _clone(cls, url: str, branch: str) -> Path:
        tmp = tempfile.mkdtemp()
        subprocess.run(
            ["git", "clone", "--depth=1", f"--branch={branch}",
             "--quiet", url, tmp],
            check=True, capture_output=True
        )
        return Path(tmp)

    @classmethod
    def _collect_files(cls, path: Path, mode: str) -> list[Path]:
        files = []
        for p in sorted(path.rglob("*")):
            if not p.is_file():
                continue
            if any(skip in p.parts for skip in cls.SKIP_DIRS):
                continue
            if any(p.name.endswith(skip.lstrip("*")) for skip in cls.SKIP_DIRS
                   if skip.startswith("*")):
                continue
            if p.stat().st_size > cls.MAX_FILE_BYTES:
                continue
            if p.suffix not in cls.INCLUDE_EXTENSIONS:
                continue
            if mode == "docs_only" and p.suffix in {".py", ".go", ".ts", ".js"}:
                continue
            if mode == "code_only" and p.suffix in {".md", ".rst", ".txt"}:
                continue
            files.append(p)
        return files

    @classmethod
    def _extract_file(cls, path: Path) -> str:
        if path.suffix == ".ipynb":
            return cls._extract_notebook(path)
        if path.suffix == ".py":
            return cls._extract_python_docstrings(path)
        return path.read_text(errors="ignore")

    @staticmethod
    def _extract_notebook(path: Path) -> str:
        """Interleave markdown and code cells — preserves pedagogical flow."""
        nb = json.loads(path.read_text(errors="ignore"))
        parts = []
        for cell in nb.get("cells", []):
            src = "".join(cell.get("source", []))
            if not src.strip():
                continue
            if cell["cell_type"] == "markdown":
                parts.append(src)
            elif cell["cell_type"] == "code":
                # Include cell output if it is short (e.g. a result)
                outputs = cell.get("outputs", [])
                out_text = ""
                for o in outputs:
                    if o.get("output_type") == "stream":
                        out_text = "".join(o.get("text", []))[:500]
                    elif "text/plain" in o.get("data", {}):
                        out_text = "".join(o["data"]["text/plain"])[:500]
                block = f"```python\n{src}\n```"
                if out_text:
                    block += f"\n\nOutput:\n```\n{out_text.strip()}\n```"
                parts.append(block)
        return "\n\n".join(parts)

    @staticmethod
    def _extract_python_docstrings(path: Path) -> str:
        """
        Extract module docstring, class docstrings, and function docstrings.
        Keeps the code structure visible without including all implementation.
        """
        import ast
        src = path.read_text(errors="ignore")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return src  # fallback to raw

        parts = []
        # Module docstring
        if (isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)):
            parts.append(tree.body[0].value.value)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                doc = ast.get_docstring(node)
                if doc:
                    kind = "class" if isinstance(node, ast.ClassDef) else "def"
                    parts.append(f"### {kind} {node.name}\n\n{doc}")

        # Also keep the actual source for code blocks
        parts.append(f"```python\n{src[:3000]}\n```")
        return "\n\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# 3. YOUTUBE EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────

class YouTubeExtractor:
    """
    Download and transcribe YouTube videos locally.

    Uses faster-whisper for transcription (runs on CPU, no API cost).
    Preserves timestamps so chunks can link back to source video.

    Playlist mode: processes each video independently,
    returns one RawSource per video for structured chunking.

    Model size guide:
      tiny   — 39M params, fast, lower accuracy for technical content
      base   — 74M params, good balance for lectures
      small  — 244M params, better for math/technical terms
      medium — 769M params, best accuracy, slower
    """

    def __init__(self, model_size: str = "base"):
        self._model = None
        self._model_size = model_size

    def _get_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                self._model_size,
                device="cpu",
                compute_type="int8",   # halves memory, negligible quality loss
            )
        return self._model

    def extract_video(self, url: str,
                      title_hint: str = "") -> RawSource:
        """Single video → RawSource with timestamped transcript."""
        with tempfile.TemporaryDirectory() as tmp:
            audio_path = Path(tmp) / "audio.mp3"
            info = self._download_audio(url, audio_path)
            title = info.get("title", title_hint or url.split("=")[-1])
            segments, duration = self._transcribe(audio_path)

        # Format: timestamp-annotated paragraphs for chunking
        text = self._format_transcript(title, segments)

        return RawSource(
            text        = text,
            metadata    = {
                "title":    title,
                "url":      url,
                "duration": duration,
                "segments": len(segments),
            },
            source_type = "youtube",
        )

    def extract_playlist(self, url: str) -> list[RawSource]:
        """
        Playlist → list of RawSource, one per video.
        Returns in playlist order so chapter numbering is preserved.
        """
        video_urls = self._get_playlist_urls(url)
        sources    = []
        for i, video_url in enumerate(video_urls, 1):
            try:
                source = self.extract_video(video_url)
                source.metadata["playlist_index"] = i
                source.metadata["playlist_url"]   = url
                sources.append(source)
            except Exception as e:
                print(f"  Skipping video {i}: {e}")
        return sources

    @staticmethod
    def _download_audio(url: str, out_path: Path) -> dict:
        """Download audio only with yt-dlp, return video info."""
        import yt_dlp

        ydl_opts = {
            "format":           "bestaudio/best",
            "postprocessors": [{
                "key":            "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }],
            "outtmpl":          str(out_path.with_suffix("")),
            "quiet":            True,
            "no_warnings":      True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        return info or {}

    def _transcribe(self, audio_path: Path) -> tuple[list[dict], float]:
        """
        Transcribe with faster-whisper.
        Returns (segments_list, total_duration_seconds).

        Each segment: {start, end, text, words: [{start, end, word}]}
        """
        model    = self._get_model()
        segments_iter, info = model.transcribe(
            str(audio_path),
            language        = "en",
            beam_size       = 5,
            word_timestamps = True,   # needed for precise chunk boundaries
            vad_filter      = True,   # skip silence — critical for lectures
            vad_parameters  = {"min_silence_duration_ms": 800},
        )
        segments = []
        for seg in segments_iter:
            segments.append({
                "start": round(seg.start, 2),
                "end":   round(seg.end,   2),
                "text":  seg.text.strip(),
            })
        return segments, info.duration

    @staticmethod
    def _format_transcript(title: str, segments: list[dict]) -> str:
        """
        Format as markdown with timestamp markers.
        Groups segments into ~3-minute paragraphs for chunking.

        Timestamp format: [MM:SS] — preserved in the chunk metadata.
        """
        lines  = [f"# {title}\n"]
        para   = []
        para_start = 0.0
        PARA_DURATION = 180.0   # 3 minutes per paragraph

        for seg in segments:
            if not para:
                para_start = seg["start"]
            para.append(seg["text"])

            if seg["end"] - para_start >= PARA_DURATION:
                mm  = int(para_start // 60)
                ss  = int(para_start % 60)
                ts  = f"[{mm:02d}:{ss:02d}]"
                lines.append(f"\n{ts} " + " ".join(para))
                para = []
                para_start = seg["end"]

        if para:
            mm = int(para_start // 60)
            ss = int(para_start % 60)
            lines.append(f"\n[{mm:02d}:{ss:02d}] " + " ".join(para))

        return "\n".join(lines)

    @staticmethod
    def _get_playlist_urls(url: str) -> list[str]:
        """Extract individual video URLs from a playlist."""
        import yt_dlp
        ydl_opts = {
            "extract_flat": True,
            "quiet":        True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        entries = info.get("entries", []) if info else []
        return [
            f"https://www.youtube.com/watch?v={e['id']}"
            for e in entries if e.get("id")
        ]


# ─────────────────────────────────────────────────────────────────────────────
# 4. WEB EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────

class WebExtractor:
    """
    Extract clean text from web articles, Substack posts, blogs, arXiv.

    Uses Crawl4AI for JavaScript-rendered pages.
    Falls back to trafilatura for static pages (fast, no browser needed).
    Handles Substack series as ordered article lists.
    Handles arXiv IDs directly.
    """

    @classmethod
    def extract_url(cls, url: str) -> RawSource:
        if "arxiv.org" in url:
            return cls._from_arxiv(url)
        if "substack.com" in url:
            return cls._from_substack(url)
        # Try trafilatura first (no browser, fast)
        text = cls._with_trafilatura(url)
        if not text or len(text.split()) < 100:
            # Fall back to Crawl4AI (handles JS-rendered content)
            text = cls._with_crawl4ai(url)
        title = cls._extract_title(url, text)
        return RawSource(
            text        = text,
            metadata    = {"url": url, "title": title},
            source_type = "web",
        )

    @classmethod
    def extract_list(cls, urls: list[str],
                     series_title: str = "") -> RawSource:
        """Extract and concatenate multiple related articles (a series)."""
        parts = []
        for i, url in enumerate(urls, 1):
            src = cls.extract_url(url)
            title = src.metadata.get("title", f"Part {i}")
            parts.append(f"# {title}\n\n{src.text}")
        combined = "\n\n---\n\n".join(parts)
        return RawSource(
            text        = combined,
            metadata    = {"series": series_title, "urls": urls},
            source_type = "web",
        )

    @staticmethod
    def _with_trafilatura(url: str) -> str:
        try:
            import trafilatura
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                return trafilatura.extract(
                    downloaded,
                    include_tables=True,
                    include_comments=False,
                    output_format="markdown",
                ) or ""
        except Exception:
            pass
        return ""

    @staticmethod
    def _with_crawl4ai(url: str) -> str:
        """Crawl4AI handles JavaScript-heavy sites (Next.js, React blogs)."""
        try:
            import asyncio
            from crawl4ai import AsyncWebCrawler

            async def _crawl():
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url=url)
                    return result.markdown or ""

            return asyncio.run(_crawl())
        except Exception:
            return ""

    @staticmethod
    def _from_arxiv(url: str) -> RawSource:
        """ArXiv: download the abstract + full paper via arXiv API."""
        import urllib.request, urllib.parse
        import xml.etree.ElementTree as ET

        # Extract arXiv ID from URL
        arxiv_id = re.search(r'(\d{4}\.\d{4,5})', url)
        if not arxiv_id:
            raise ValueError(f"Cannot extract arXiv ID from {url}")
        aid = arxiv_id.group(1)

        # Fetch abstract
        api_url = f"https://export.arxiv.org/api/query?id_list={aid}"
        with urllib.request.urlopen(api_url) as r:
            tree = ET.parse(r)
        ns    = "http://www.w3.org/2005/Atom"
        entry = tree.find(f"{{{ns}}}entry")
        title   = entry.find(f"{{{ns}}}title").text.strip()
        summary = entry.find(f"{{{ns}}}summary").text.strip()

        # Try to download PDF via arXiv
        pdf_url = f"https://arxiv.org/pdf/{aid}.pdf"
        text    = f"# {title}\n\n## Abstract\n\n{summary}\n\n"

        # Attempt PDF extraction
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = Path(tmp) / f"{aid}.pdf"
            try:
                urllib.request.urlretrieve(pdf_url, pdf_path)
                pdf_text = BookExtractor._from_pdf(str(pdf_path))
                text += pdf_text
            except Exception:
                pass  # Use abstract only

        return RawSource(
            text        = text,
            metadata    = {"title": title, "arxiv_id": aid, "url": url},
            source_type = "web",
        )

    @staticmethod
    def _from_substack(url: str) -> RawSource:
        """
        Substack posts are static HTML — trafilatura handles them well.
        For full newsletters, strip the email-specific boilerplate.
        """
        text = WebExtractor._with_trafilatura(url)
        # Remove Substack email footer patterns
        text = re.sub(
            r'Subscribe\s+to\s+\w+.*?$', '', text,
            flags=re.IGNORECASE | re.DOTALL
        )
        title = WebExtractor._extract_title(url, text)
        return RawSource(
            text        = text,
            metadata    = {"url": url, "title": title},
            source_type = "web",
        )

    @staticmethod
    def _extract_title(url: str, text: str) -> str:
        """Try to extract title from first heading line."""
        for line in text.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return url.split("/")[-1].replace("-", " ").replace("_", " ")
