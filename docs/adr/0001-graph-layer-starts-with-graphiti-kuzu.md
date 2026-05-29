# Graph Layer Starts With Graphiti And Kuzu

The Graph Layer will start with Graphiti over Kuzu because the product needs temporal learning memory and source provenance early, while remaining local-first, Docker-runnable, and easy to migrate. The application owns its Learning Graph, Source Graph, and Memory Graph contracts; Graphiti and Kuzu are first implementations behind those contracts, with FalkorDB or another graph backend deferred until graph complexity or deployment needs justify it.

## Considered Options

- Graphiti with FalkorDB first: stronger service-oriented GraphRAG path, but adds more operational and licensing considerations before the graph needs that complexity.
- Custom Kuzu graph first: maximum schema ownership, but delays temporal context-graph behavior that is useful for learner memory.
- Supporting both FalkorDB and Kuzu from v1: cleanest adapter story, but too much early surface area before real graph workloads exist.
