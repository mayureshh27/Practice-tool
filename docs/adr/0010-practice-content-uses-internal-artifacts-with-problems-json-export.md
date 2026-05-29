# Practice Content Uses Internal Artifacts With Problems Json Export

Practice content will use a richer internal PracticeArtifact model that records source references, concept identifiers, workflow identifiers, citations, graph links, evaluation scores, artifact status, and a typed payload for the generated practice content. `problems.json` remains a compatibility export for the current PracDaGo UI while the internal schema evolves toward custom and separately typed artifacts.

## Consequences

The existing UI can continue to consume its current problem shape, but ingestion and workflow outputs should not be limited by that shape. Future artifacts such as quizzes, reports, mind maps, flashcards, and custom user-defined outputs can share the artifact base while defining their own payload schemas.
