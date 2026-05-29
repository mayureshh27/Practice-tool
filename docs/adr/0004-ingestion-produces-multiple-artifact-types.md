# Ingestion Produces Multiple Artifact Types

The Ingestion Harness will produce source registry records, normalized documents, stable chunks with citations, concept and graph facts, practice exercises, and structured lessons as first-class outputs. `problems.json` remains a compatibility export for the existing practice UI, while NotebookLM-style artifacts such as mind maps, reports, quizzes, flashcards, slide decks, and data tables are generated on demand through customizable AI workflows rather than always produced during ingestion.

## Consequences

Small learner inputs should still be able to trigger exercise, lesson, or explanation generation through workflow templates. The ingestion contract must preserve enough source, chunk, citation, and concept metadata for later workflows to generate new artifacts without re-extracting the original source.
