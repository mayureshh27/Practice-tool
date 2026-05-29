# Ingestion Pipeline

Turns any technical content into structured practice problems.

## Supported sources

| Source | Command | Best for |
|---|---|---|
| PDF book | `book` | Textbooks, monographs |
| LaTeX source | `book` | Math books with preserved equations |
| YouTube video | `youtube` | Lectures, tutorials |
| YouTube playlist | `playlist` | Lecture series |
| GitHub repo | `github` | Libraries, frameworks, documentation |
| Web article | `web` | Blog posts, Substack, arXiv |
| Raw text / stdin | `text` | Paste anything |

## Quick start

```bash
# 1. Install
pip install -e ".[youtube]"          # YouTube support
pip install -e ".[docling]"          # OCR for scanned PDFs
pip install -e ".[all]"              # Everything

# 2. Build sandbox image (one time)
docker build -f Dockerfile.sandbox -t learning-platform:python .

# 3. Copy and fill env
cp .env.example .env
# Set ANTHROPIC_API_KEY (minimum required)

# 4. Run ingestion
python -m ingestion.cli book path/to/Strang_LA.pdf \
    --chapter la1 --title "Vectors and Spaces" \
    --api-key $ANTHROPIC_API_KEY
```

## Mode: exercise-first (default for books)

For deep maths books, `--mode exercise-first` extracts verbatim
exercises from the book first, generates problems from them, then
fills gaps from section text.

This gives the highest quality because the author already designed the
exercise — we just wrap it in our schema and validate it runs.

```bash
python -m ingestion.cli book Strang_LA.pdf \
    --chapter la1 \
    --mode exercise-first \
    --api-key $ANTHROPIC_API_KEY
```

## YouTube — local transcription (no API cost)

```bash
# Single lecture
python -m ingestion.cli youtube \
    "https://youtube.com/watch?v=7UJ4CFRGd-U" \
    --chapter la1 \
    --whisper-size small \
    --api-key $ANTHROPIC_API_KEY

# Full lecture series
python -m ingestion.cli playlist \
    "https://youtube.com/playlist?list=PL49CF3715CB9EF31D" \
    --chapter la1 \
    --title "MIT 18.06 Linear Algebra"
```

Whisper model size guide:
- `tiny`   — 39M params, fastest, lower accuracy for equations
- `base`   — 74M params, good balance (default)
- `small`  — 244M params, better for math/technical terms
- `medium` — 769M params, best accuracy, 4× slower than base

## Gap analysis

After ingesting several chapters, find what is missing:

```bash
python -m ingestion.cli gaps \
    --chapter la3 \
    --api-key $ANTHROPIC_API_KEY
```

Outputs: `data/gaps_la3.json` with suggested problems and their tags.

Fill a gap by piping the suggestion to stdin:

```bash
echo "Compute the SVD of a 2x3 matrix and identify rank from singular values" | \
    python -m ingestion.cli text - \
    --chapter la3 \
    --api-key $ANTHROPIC_API_KEY
```

## Review queue

Problems below the quality threshold are held in `data/pending_review.json`.
Replay them at any time:

```bash
python -m ingestion.cli review --chapter la1
```

Actions: `a`pprove, `e`dit (opens $EDITOR), `r`eject, `s`kip, `v`iew.

## Running tests

```bash
# Fast tests (no Docker, no API key)
pytest tests/test_ingestion.py -v

# Include Docker sandbox tests
pytest tests/test_ingestion.py -v -m slow

# Skip slow tests explicitly
pytest tests/test_ingestion.py -v -m "not slow and not e2e"
```

## Pipeline stages

```
Source → Normalise → Structure → Chunk → Generate → Validate → Retry → Dedup → Review → Merge
  1          2           3          4        5           6          7       8        9       10
```

Each stage is a plain Python class you can call independently for debugging:

```python
from ingestion.processing.normaliser import Normaliser
from ingestion.processing.chunker    import Chunker, Strategy
from ingestion.processing.structure  import BookStructureDetector

text = open("chapter.txt").read()
doc  = Normaliser.normalise(text, source_type="book")
book = BookStructureDetector.detect(doc.text, title="My Book")
print(f"{book.total_exercises} exercises, {book.total_theorems} theorems")

chunks = Chunker().chunk(doc, Strategy.HIERARCHICAL)
print(f"{len(chunks)} chunks, first: {chunks[0].section_title}")
```

## Environment variables

See `.env.example` for all options. Minimum required:

```
ANTHROPIC_API_KEY=sk-ant-...
GOPRAC_SANDBOX_IMAGE=learning-platform:python
```

## Cost guide

Approximate cost per chapter (10-20 problems):

| Model | Cost | Quality |
|---|---|---|
| claude-sonnet-4-20250514 | ~$0.30–0.80 | Best for maths |
| claude-haiku-4-5-20251001 | ~$0.03–0.08 | Good for code/docs |
| gpt-4o | ~$0.20–0.60 | Strong alternative |
| gemini/gemini-1.5-flash | ~$0.01–0.03 | Cheap, good for bulk |

Use `--max-chunks 10` to limit cost during testing.
