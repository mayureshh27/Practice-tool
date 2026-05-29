# PRD: Memory Layer — Adaptive Practice Workspace

## Problem Statement

The Adaptive Practice Workspace needs a memory layer that makes the Socratic tutor aware of the
learner's history across sessions — which concepts they have practiced, where they repeatedly fail,
which sources they have studied, and how mastery has evolved over time. Without this layer the tutor
starts blind on every request: it cannot detect blind spots, cannot target weak prerequisites, cannot
avoid re-explaining concepts the learner has already mastered, and cannot compress prior session
history into context without losing attribution.

Generic memory tools (Mem0, Zep Cloud, LangMem, Cognee cloud) do not fit the platform's needs for
four structural reasons. First, they let the model decide what to store, making the memory
non-deterministic and hard to audit. Second, they flatten all memory into embedding-retrievable
string factoids, which erases the causal chain linking a specific attempt to a specific concept to a
specific source. Third, they merge source-content retrieval with learner-state retrieval into one
vector store, making it impossible to prevent source noise from polluting the learner-state context
slot. Fourth, they have no concept of typed domain events — none of them know what a
`PracticeAttempted` or `BlindSpotDetected` event is.

The platform therefore needs its own MemoryStore built from first principles as a domain-event log,
backed by SQLite as the auditable source of truth, with Graphiti/Kuzu as a temporal knowledge graph
for cross-entity queries, and Qdrant kept strictly for source-chunk retrieval behind a separate
RetrievalLayer contract.

## Solution

Build a MemoryStore module that records seven typed domain events from the practice loop — written
by the harness, never by the model — and exposes a read interface that the Context Engineering Layer
calls to assemble the learner memories slot and the graph facts slot in the fixed-slot context
window.

The MemoryStore is backed by SQLite (typed event rows with full foreign-key attribution to session,
concept, source, artifact, and attempt identifiers). The GraphLayer, backed by Graphiti over Kuzu,
maintains a temporal knowledge graph whose nodes are Concept, Source, Exercise, Attempt, Session,
and BlindSpot entities. Every mastery score lives on a Concept node and is timestamped by Graphiti
so point-in-time queries are possible. Source-chunk retrieval stays entirely in Qdrant behind the
RetrievalLayer — it never stores memory events.

The harness writes a ConceptMasteryUpdated event after every PracticeAttempted event using a
deterministic rule (not an LLM call). It writes a BlindSpotDetected event when the rule threshold
is crossed. It writes a SessionSummaryCreated event at session close using one LLM call. The
Context Engineering Layer reads from the MemoryStore via `get_learner_context()` and from the
GraphLayer via `get_concept_context()`, assembling the named slots within hard token budgets before
every model call.

## User Stories

1. As a learner, I want the tutor to know which concepts I have practiced before, so that it does
   not waste context explaining fundamentals I have already mastered.
2. As a learner, I want the tutor to detect when I keep failing the same type of exercise, so that
   it can identify my blind spot and target remediation.
3. As a learner, I want the tutor to know which sources I have ingested, so that its hints can
   reference material I actually have access to.
4. As a learner, I want hint context to include how many times I have requested hints on the
   current concept across past sessions, so that the tutor can escalate appropriately.
5. As a learner, I want the system to remember that I failed an exercise three sessions ago even if
   I do not remember, so that the workspace can surface it as unresolved.
6. As a learner, I want my mastery of prerequisite concepts to influence which exercises the system
   recommends, so that I am not sent to advanced material before I am ready.
7. As a learner, I want a session summary to persist across sessions, so that the tutor does not
   need to reload the full conversation history to understand my current state.
8. As a learner, I want session summaries to be compressed but attributed, so that I can verify
   what the system believes about my progress.
9. As a learner, I want blind spots to be cleared once I demonstrate mastery, so that old failures
   do not permanently constrain recommendations.
10. As a learner, I want the tutor to reference graph facts about concept prerequisites when I am
    stuck, so that it can identify which gap in my foundation is causing the struggle.
11. As a learner, I want the system to know that "state space representation" and "state-space
    models" are the same concept, so that mastery earned in one exercise transfers to another.
12. As a learner, I want my mastery history to be queryable at a point in time, so that I can
    understand how my understanding of a concept evolved.
13. As a learner, I want the context assembled for every tutor call to stay within a conservative
    token budget, so that the tutor remains precise and does not hallucinate from irrelevant context.
14. As a learner, I want the learner memories context slot to include my active blind spots,
    recent mastery deltas, and the previous session summary, so that the tutor has the right signal
    in a compact form.
15. As a learner, I want graph facts in the context slot to include prerequisite chains and gap
    concepts, so that the tutor can trace exactly which foundational concept I am missing.
16. As a developer, I want all seven event types represented as typed Pydantic models, so that
    malformed events fail at the boundary before reaching the database.
17. As a developer, I want every event row to carry foreign-key identifiers for session, concept,
    source, artifact, and attempt, so that SQL joins can reconstruct the full causal chain.
18. As a developer, I want the MemoryStore to expose a narrow Python interface, so that the
    storage backend can be swapped without changing agent or workflow code.
19. As a developer, I want concept mastery to be updated by a deterministic rule after each
    attempt, so that the mastery scores are auditable without replaying LLM calls.
20. As a developer, I want blind spot detection to be a deterministic rule over the event log,
    so that thresholds are visible, configurable, and testable without an LLM.
21. As a developer, I want session summaries written by a single LLM call at session close, so
    that the cost and latency of summarization is paid once per session, not per tutor call.
22. As a developer, I want the session summary to be a typed Pydantic model, so that missing
    fields in the LLM output are caught before the summary is stored.
23. As a developer, I want the GraphLayer to expose product-owned methods rather than raw Cypher,
    so that Graphiti and Kuzu remain replaceable implementations behind the contract.
24. As a developer, I want concept identity resolved at ingestion time, so that mastery scores are
    not split across two nodes for what is logically one concept.
25. As a developer, I want MemoryStore, GraphLayer, and RetrievalLayer injected as dependencies
    into Pydantic AI agents, so that agents are independently testable with mock implementations.
26. As a developer, I want the context builder to emit token budget diagnostics, so that I can
    identify which slot is bloating the context window during debugging.
27. As a developer, I want the system slot in the context window to carry a hard budget that is
    never silently truncated, so that system rules are always present in full.
28. As a developer, I want every memory event to be written in a Pydantic Evals test, so that
    regressions in event attribution are caught before merging.
29. As a developer, I want JSONL result logs from every eval run, so that I can compare mastery
    scoring behaviour across prompt and rule changes.
30. As a developer, I want the MemoryStore to support querying active blind spots, recent mastery
    deltas, and the last session summary in a single call, so that context assembly has one
    round-trip to the store rather than three.

## Implementation Decisions

### Deep modules

The following modules encapsulate significant complexity behind a stable, narrow interface and
should be treated as deep modules — changes to their internals should not propagate to callers.

**MemoryStore**
The central interface. Callers never touch SQLite directly. Exposes:
- `record_event(event: MemoryEvent) -> None` — writes any of the 7 typed events
- `get_learner_context(concept_ids, session_id) -> LearnerContext` — returns compressed learner
  state for context assembly: active blind spots, recent mastery deltas, prior session summary text
- `get_session_summary(session_id) -> SessionSummary | None`
- `get_blind_spots(resolved=False) -> list[BlindSpot]`

**GraphLayer**
Product-owned graph interface. Exposes:
- `extract_and_link_concepts(source_id, concept_candidates) -> list[ConceptNode]`
- `update_mastery(concept_id, new_score, trigger_event_id, timestamp)`
- `get_concept_context(concept_ids) -> ConceptContext` — prereq chain, gap concepts, mastery scores
- `link_exercise_to_concepts(exercise_id, concept_ids)`
- `detect_prerequisite_gaps(concept_ids) -> list[ConceptNode]`

Graphiti handles temporal semantics (timestamped edges, point-in-time queries). Kuzu is the
embedded local storage. Neither is imported outside this module.

**RetrievalLayer**
Source-chunk interface only. Never used for memory event retrieval.
- `search(query, source_ids, top_k, filters) -> list[Chunk]`
- `index_chunks(chunks: list[Chunk]) -> None`

**ContextBuilder**
Assembles the fixed named slots into a model-ready messages list.
Slots (default budgets):
- `system` — hard limit, never truncated
- `workflow_template` — ~2 000 tokens
- `learner_memories` — ~2 000 tokens (from MemoryStore)
- `graph_facts` — ~1 500 tokens (from GraphLayer)
- `retrieved_source_chunks` — ~8 000 tokens default, larger in deep-source mode (from RetrievalLayer)
- `history_summary_and_tail` — ~3 000 tokens (summary from MemoryStore, tail from session state)
- `tools` — variable
- `user_request` — variable
Emits token budget diagnostics on every assembly call.

### Seven typed event models

All seven are Pydantic BaseModel subclasses with a shared `MemoryEvent` base carrying
`event_id`, `event_type`, `recorded_at`. Every event carries the foreign-key identifiers
appropriate to its position in the causal chain.

- `SourceIngested` — source_id, source_type, domain, subject, chunk_count, concept_candidates,
  ingestion_duration_ms, eval_scores
- `ArtifactGenerated` — artifact_id, artifact_type, source_ids, concept_ids, workflow_id,
  template_id, eval_scores, status
- `PracticeAttempted` — attempt_id, exercise_id, session_id, concept_ids, attempt_number, passed,
  time_on_task_seconds, test_results (list of pass/fail per test case)
- `HintRequested` — hint_id, attempt_id, session_id, exercise_id, hint_number, hint_type,
  concept_ids_activated
- `BlindSpotDetected` — blind_spot_id, concept_id, confidence_score, evidence_event_ids,
  detected_at, resolved_at (nullable)
- `ConceptMasteryUpdated` — mastery_event_id, concept_id, old_mastery_score, new_mastery_score,
  trigger_event_id (the attempt_id that caused the update)
- `SessionSummaryCreated` — summary_id, session_id, start_time, end_time, concepts_practiced,
  exercises_attempted, hints_requested, mastery_deltas (dict[concept_id, float]), summary_text,
  model_used

### Mastery update rule (deterministic, not LLM)

After every `PracticeAttempted` event:
- pass → new_score = min(old_score + 0.10, 1.0)
- fail → new_score = max(old_score - 0.05, 0.0)

The rule is a pure Python function in a `rules.py` module. It is the only place mastery arithmetic
lives. It must not call the LLM. Emit a `ConceptMasteryUpdated` event. Update the Concept node in
the graph via `GraphLayer.update_mastery()`.

### Blind spot detection rule (deterministic, not LLM)

After every `PracticeAttempted` event, run the blind spot check over the event log for the
concept_ids exercised:
- Condition: an exercise on this concept has been attempted ≥ 3 times across distinct sessions,
  the most recent attempt did not pass, and hint count per attempt is not decreasing.
- If met: emit `BlindSpotDetected`. Write the evidence_event_ids. Mark resolved_at=None.
- Clear the blind spot (set resolved_at) on the next `ConceptMasteryUpdated` where the new score
  crosses 0.7 for that concept.

### Concept identity resolution (resolved at ingestion, not at query time)

During ingestion the IngestionHarness calls the concept extraction step, which returns candidate
concept names with aliases. Before creating a new Concept node the GraphLayer checks for existing
nodes whose canonical name or aliases overlap (fuzzy match, threshold configurable). If a match
is found the existing node is reused and the new alias is added. If no match, a new node is
created with the canonical name. This decision is made once, durably, and never revisited at query
time.

This is an ADR-worthy decision: hard to reverse (re-ingesting all sources to reassign concept IDs
is expensive), surprising without context (why doesn't the graph create a new node for every new
name?), and the result of a real trade-off (runtime resolution via graph traversal would lose
mastery continuity across sources).

### Session summary LLM call

At session close the SessionSummaryAgent (a Pydantic AI agent) receives the full event list for
the session and returns a `SessionSummaryCreated` Pydantic model. The prompt is a workflow
template stored in SQLite and editable by the learner. The model is configurable (Haiku for cost,
Sonnet for richer summaries). The agent does not have access to the MemoryStore or GraphLayer —
it receives a serialised event list only, keeping it stateless and testable.

### Context assembly as a read-only pull

The ContextBuilder never calls `MemoryStore.record_event()`. It only reads. The practice surface
and tutor workflow are responsible for writing events after the model responds. This separation
means ContextBuilder is a pure function of its inputs and is trivially testable.

### Deep-source mode boundary

Deep-source mode expands the `retrieved_source_chunks` slot to the model's full window. It is
activated explicitly by the workflow template, never by the context builder itself. Default mode
caps total context at 30 000–40 000 tokens. Deep-source mode is only valid for ingestion,
research, and source-synthesis workflows — never for the interactive tutor or hint generation paths.

### Tool placement summary

- Pydantic AI — agent runtime for all agents (tutor, SessionSummaryAgent, IngestionHarness)
- Pydantic (core) — all 7 event models, LearnerContext, ConceptContext, all output schemas
- Instructor — selective: concept extraction step at ingestion, eval judging where retry on
  structured output failure materially reduces failure rate
- DSPy — deferred until enough real eval examples exist to optimize prompts meaningfully
- LangGraph — deferred until workflow steps need durable checkpoint/resume across sessions
- SQLite — event log, source of truth, also stores workflow templates and artifact metadata
- Qdrant — source chunks only behind RetrievalLayer; never used for event storage
- Graphiti — temporal graph engine behind GraphLayer; handles timestamped mastery updates
- Kuzu — embedded local graph storage that Graphiti writes to
- Neo4j — upgrade path if graph complexity or deployment needs grow beyond Kuzu
- Cognee — not a dependency; its ingestion pipeline patterns are inspiration only
- Zep Cloud — rejected; data must remain local
- Mem0 OSS — the add/update/delete/noop algorithm is a useful pattern for ingestion-time concept
  deduplication; not used as a memory provider

## Testing Decisions

A good test verifies the external behaviour of a module through its public interface. It does not
assert on private method calls, internal state, or implementation-specific SQL queries. If a test
breaks because the storage backend changed but the behaviour did not, the test was wrong.

**MemoryStore**
- Record each of the 7 event types and verify `get_learner_context()` returns a `LearnerContext`
  that reflects them.
- Verify that `get_blind_spots(resolved=False)` returns only unresolved blind spots.
- Verify that a `ConceptMasteryUpdated` event that crosses the 0.7 threshold causes the
  associated BlindSpot's `resolved_at` to be set.
- Verify that `get_learner_context()` returns only the most recent session summary for the
  learner memories slot, not all summaries.
- Verify that mastery deltas are computed correctly across multiple `ConceptMasteryUpdated`
  events for the same concept in one session.

**GraphLayer**
- Verify concept insertion: a new concept name creates a new node; a name that matches an
  existing node's alias reuses the existing node.
- Verify `update_mastery()` timestamps the edge (Graphiti temporal behaviour) and that
  `get_concept_context()` reflects the new score.
- Verify `get_concept_context()` returns the full prerequisite chain for a concept with
  transitive prerequisites.
- Verify `detect_prerequisite_gaps()` returns only prerequisites with mastery below threshold.
- Verify that GraphLayer methods are callable without Graphiti running (mock Graphiti in unit
  tests; integration tests use a real local Kuzu instance).

**RetrievalLayer**
- Verify `search()` returns chunks filtered by source_id, not chunks from unrelated sources.
- Verify `search()` returns chunks ranked by semantic relevance, not insertion order.
- Verify empty-result behaviour when no source is indexed.
- Verify that chunks carry citation metadata (source_id, chunk_index, page_or_timestamp).

**ContextBuilder**
- Verify slot ordering: system slot is always first.
- Verify the system slot is never truncated even when total budget is exceeded.
- Verify that deep-source mode is only active when the workflow template explicitly enables it.
- Verify token budget diagnostics are emitted on every call.
- Verify that the total assembled context does not exceed the configured budget in default mode.

**Mastery update rule**
- Unit test: pass on first attempt → score increases from 0 to 0.10.
- Unit test: fail → score decreases, floor at 0.0.
- Unit test: repeated passes → score reaches 1.0 and stays there.
- Unit test: pass event on multiple concepts → each concept updates independently.

**Blind spot detection rule**
- Unit test: 3 failed attempts across 3 distinct sessions triggers `BlindSpotDetected`.
- Unit test: 3 failed attempts in the same session does not trigger.
- Unit test: mastery crossing 0.7 sets `resolved_at` on the matching BlindSpot.
- Unit test: a subsequent fail after resolution creates a new BlindSpot event.

**SessionSummaryAgent**
- Golden case: given a serialised event list for a known session, the returned
  `SessionSummaryCreated` model has non-empty `summary_text`, correct `concepts_practiced` list,
  and `mastery_deltas` that match the `ConceptMasteryUpdated` events in the input.
- Verify the agent fails fast (Pydantic validation error) if the LLM returns a summary without
  `summary_text`.

**Eval gates (Pydantic Evals)**
- Hint no-leakage eval: the tutor response when a hint is requested does not contain the solution
  code or a direct answer.
- Hint specificity eval: the tutor response references the learner's submitted code, not a generic
  hint.
- Context slot eval: for a given exercise and learner state fixture, the assembled context
  contains the expected blind spot mention in the learner memories slot.
- Citation grounding eval: tutor responses that reference source material include a citation that
  traces to a real ingested chunk.

JSONL result logs must be written for all eval runs. The suite must cover at least 5 golden cases
per workflow before agents are allowed to modify its prompts or contracts.

## Out of Scope

- User preference memory (preferred explanation style, preferred difficulty) — deferred until the
  event log is mature enough to derive preferences from behaviour.
- Organisation-level or multi-user memory — the platform is single-user, local-first.
- LLM-decided memory writes — the harness always decides what to store.
- DSPy prompt optimisation — deferred until sufficient real eval examples exist.
- LangGraph durable orchestration — deferred until workflows need checkpoint/resume.
- Zep Cloud or Cognee as memory providers — data must remain local.
- Hosted vector or graph databases — Qdrant and Kuzu run locally in Docker.
- Memory portability or export — out of scope for v1.
- Preference-based context personalisation (e.g. "I prefer code before theory") — deferred.
- Real-time mastery dashboards in the UI — the MemoryStore exposes the data; UI is a separate task.

## Further Notes

**The fifth memory demand.** The standard four-type taxonomy (in-context, episodic, semantic,
procedural) covers approximately 60% of this platform's memory demands. The missing 40% is causal
mastery attribution: the ability to answer "which attempt caused which mastery change, via which
source, on which concept, in which session." No off-the-shelf memory framework has this concept.
It must be built. It is the core value of the MemoryStore.

**Semantic similarity is not domain relevance.** The Zep/Daniel workshop demonstration showed that
embedding all memory as flat strings and retrieving by cosine similarity causes irrelevant facts to
pollute context. This is not fixable by better embeddings — it is a category error. Memory events
must be retrieved by typed entity ID and SQL join, not by semantic search. Qdrant is the right tool
for source chunks because source chunks are genuinely text-similarity problems. Memory events are
not.

**Cognee as inspiration, not dependency.** Cognee's three-stage capture → model → recall pipeline
and its graph-first ingestion are the right mental model for the IngestionHarness stages. Their
source code is worth reading. They are not suitable as a dependency because they own the memory
contract, their entity schemas cannot express typed domain events, and they are moving toward cloud
hosting.

**Concept identity is the earliest irreversible decision.** If two Concept nodes are created for
what is logically one concept (because two sources name it differently), mastery scores split and
graph traversal queries break. This must be resolved at ingestion time. An ADR should be filed
before the first source is processed.

**The graph spans all stores.** The GraphLayer is not a separate knowledge base — it is the index
over all entity relationships across SQLite, Qdrant, and Graphiti/Kuzu. Cross-store queries (e.g.
"which concepts does this learner have blind spots in AND which Qdrant chunks contain remediation
material for those concepts?") are only possible through graph traversal. This is why the graph
layer is a first-class architectural component, not an add-on.