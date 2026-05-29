# Handoff: Adaptive Practice Workspace Planning

## Purpose

This handoff is for a fresh agent continuing the Learning Platform / Practice-tool work after the product grilling and PRD synthesis session.

Do not replay the full ideation. The decisions have been captured in repo artifacts. Continue from those documents.

## Primary Artifacts To Read First

- `D:\Robotics\Learning-Platform\Practice-tool\docs\prd-adaptive-practice-workspace.md`
- `D:\Robotics\Learning-Platform\Practice-tool\CONTEXT.md`
- `D:\Robotics\Learning-Platform\Practice-tool\docs\adr\`
- Original broad ideation source: `D:\Robotics\Learning-Platform\Handoff.md`

## Current Product Direction

The product is an Adaptive Practice Workspace, not a generic chatbot or broad AI OS. It expands the existing PracDaGo practice app into a Codex/Claude/NotebookLM-inspired local-first workspace.

Core loop:

1. Ingest Learning Sources.
2. Normalize and chunk them.
3. Store source/chunk/citation metadata.
4. Extract concepts and graph facts.
5. Generate lessons, explanations, exercises, quizzes, and later richer artifacts.
6. Practice through the existing PracDaGo-style UI.
7. Use Socratic tutor/context/memory/graph to guide learning.
8. Record memory events and mastery changes.

## Decisions Already Captured

See ADRs in `D:\Robotics\Learning-Platform\Practice-tool\docs\adr\`.

Important locked decisions:

- Graph starts with Graphiti + Kuzu behind `GraphLayer`.
- Retrieval starts with Qdrant behind `RetrievalLayer`.
- AI runtime starts with Pydantic AI.
- LiteLLM is an optional model adapter, not a required local gateway.
- Instructor is selective for extraction/eval/structured retry paths.
- Ingestion produces multiple artifact types, not only `problems.json`.
- Shared Learning Memory starts with source, artifact, practice, hint, blind spot, mastery, and session-summary events.
- Context Builder uses fixed slots with controlled retrieval.
- Default context budget is conservative; deep-source mode is explicit.
- Workflows use structured templates with editable prompts.
- Practice content uses an internal artifact model and exports to `problems.json`.
- Eval gates use Pydantic Evals and layer-specific checks.
- Work should start with vertical tracer bullets, then layer expansion.

## Codebase Notes

Main repo appears to be:

- `D:\Robotics\Learning-Platform\Practice-tool`

Workspace root `D:\Robotics\Learning-Platform` itself is not the Git repo.

Existing useful code:

- `Practice-tool\frontend` contains the existing React/Vite PracDaGo UI.
- `Practice-tool\backend` contains the current backend.
- `Practice-tool\ingestion-pipeline` contains a strong prototype ingestion pipeline.

The ingestion prototype already has:

- extractors for PDF/LaTeX/EPUB/text, YouTube URL transcription, GitHub, web/arXiv
- normalizer
- chunker
- structure detector
- generator using Pydantic/Instructor/LiteLLM
- validator, retry, dedup, review queue, catalog merger
- tests for major stages

Known ingestion gaps relative to the PRD:

- Add PPT/DOCX extractors.
- Support uploaded user transcripts for video/playlist instead of assuming YouTube download/transcription.
- Promote output from `GeneratedProblem -> problems.json` to source registry, normalized docs, chunks, citations, graph facts, lessons, artifacts, and compatibility export.
- Replace Chroma-oriented assumptions with Qdrant behind `RetrievalLayer`.
- Keep Graphiti/Kuzu behind product-owned `GraphLayer`.

## Suggested Next Session Focus

Recommended next step: convert the PRD into independently grabbable implementation issues or a phased architecture plan.

Best first tracer bullet:

Ingest one source into the new contract and produce one usable practice artifact:

1. Create schema/contracts for source registry, chunk, artifact, memory event.
2. Adapt one existing ingestion path, likely PDF or uploaded transcript.
3. Store source/chunk metadata in SQLite.
4. Index chunks through `RetrievalLayer` abstraction.
5. Emit concept/graph facts through `GraphLayer` abstraction, even if thin.
6. Generate a `PracticeArtifact`.
7. Export compatible `problems.json`.
8. Add Pydantic Evals/golden tests for the workflow.

## Suggested Skills

- `to-issues`: break the PRD into implementation issues.
- `tdd`: build the first tracer bullet with test-first contracts.
- `diagnose`: use only if current generated/vibe-coded code fails or conflicts with the PRD.
- `improve-codebase-architecture`: use after the tracer bullet to identify consolidation/refactoring opportunities.
- `grill-with-docs`: use if a future architectural choice conflicts with `CONTEXT.md` or the ADRs.
- `setup-matt-pocock-skills`: rerun if issue tracker setup is needed before creating GitHub/local issues.

## Warnings

The working tree was already dirty. Do not revert unrelated files. At the end of the prior session, `git status --short` showed many existing modified/untracked files, including backend/frontend changes, PDFs, ingestion pipeline files, scripts, scratch files, and the newly created docs.

PowerShell also reported:

`warning: unable to unlink 'D:/Robotics/Learning-Platform/Practice-tool/.git/index.lock': Invalid argument`

A future agent should inspect whether `.git/index.lock` still exists before running git operations that need the index.

## Sensitive Data

No API keys or secrets were provided in the planning session.
