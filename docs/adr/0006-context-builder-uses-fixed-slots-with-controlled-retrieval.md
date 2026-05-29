# Context Builder Uses Fixed Slots With Controlled Retrieval

The Context Engineering Layer will use fixed named slots with hard budgets for system rules, skills, memories, tools, history, examples, and the user message, while allowing dynamic retrieval only inside named slots. This preserves the anti-bloat and anti-poisoning benefits of a deterministic context plan, while leaving room for retrieval from Qdrant, Graphiti/Kuzu, SQLite memory events, and workflow templates as the product evolves.

## Consequences

The system slot is a hard budget and must not be silently truncated. Other slots may be trimmed with usage diagnostics. The implementation should adapt the handoff's ContextBuilder idea but depend on product contracts such as RetrievalLayer, GraphLayer, MemoryStore, ModelRouter, and ToolRegistry rather than directly depending on Chroma, mem0, or provider-specific clients.
