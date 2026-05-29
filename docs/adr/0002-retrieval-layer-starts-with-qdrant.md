# Retrieval Layer Starts With Qdrant

The Retrieval Layer will start with Qdrant because the product is a Docker-runnable adaptive practice workspace that needs filtered retrieval across books, videos, repositories, notes, subjects, chapters, and concepts, with a plausible later deployment path. Application code depends on a Retrieval Layer contract rather than Qdrant directly so LanceDB, pgvector, or another retrieval backend can replace or complement Qdrant later.

## Considered Options

- LanceDB first: simpler embedded local experience, but less aligned with the dockerized service ecosystem and deployment path.
- Kuzu or Graphiti as retrieval: attractive for graph expansion, but it would mix document retrieval with graph memory too early.
- SQLite FTS first: simple and inspectable, but too limited for heavy multi-source semantic retrieval.
