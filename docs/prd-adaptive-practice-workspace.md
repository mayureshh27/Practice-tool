# PRD: Adaptive Practice Workspace

## Problem Statement

The learner is building a serious robotics and AI engineering learning practice, but the required material is scattered across books, PDFs, slide decks, Word documents, YouTube lectures, transcripts, GitHub repositories, documentation sites, chats, notes, code editors, and ad hoc generated exercises. Existing tools are helpful in isolation, but they do not share context, memory, source provenance, mastery state, or a structured practice loop.

The learner needs a local-first Adaptive Practice Workspace that can ingest Learning Sources, organize them by domain, subject, chapter, and topic, generate high-quality lessons and practice exercises, provide Socratic tutoring, run code safely, track Blind Spots, and evolve toward richer agentic workflows without becoming a generic chatbot or a fragile RAG wrapper.

## Solution

Build a Docker-runnable, local-first Adaptive Practice Workspace around the existing PracDaGo practice primitives and the current ingestion prototype. The first product spine is practice-centered: select Learning Sources, create Ingestion Artifacts, generate lessons and exercises, solve them in a Practice Surface, receive hints, run sandboxed code, update Shared Learning Memory, and connect concepts through a Knowledge Graph.

The product should feel like a hybrid of the current practice UI, Codex/Claude-style workspace navigation, and NotebookLM-style source and artifact management. The UI uses a Workspace Shell with persistent left navigation, a central Practice Surface, and dockable side and bottom panels for Resource Manager, tutor chat, graph, artifacts, terminal, output, and optional IDE-like tools.

The durable product asset is the Harness: layer contracts, evals, prompts, storage, tools, memory events, and workflow templates that make learning behavior repeatable, inspectable, and model-agnostic. Individual model providers, vector stores, graph backends, and workflow implementations must remain replaceable behind Layer Contracts.

## User Stories

1. As a learner, I want to import PDFs, books, slide decks, Word documents, uploaded video transcripts, GitHub repositories, and documentation sources, so that my robotics learning material lives in one place.
2. As a learner, I want each source organized by domain, subject, chapter, and topic, so that I can study across a long multi-month plan without losing structure.
3. As a learner, I want to select multiple sources like a NotebookLM notebook, so that generated exercises and lessons can draw from a chosen source set.
4. As a learner, I want the system to normalize and chunk each source with citations, so that every generated artifact can trace back to its evidence.
5. As a learner, I want source chunks embedded and searchable, so that tutor responses and workflows use relevant context instead of entire documents.
6. As a learner, I want concepts and prerequisites extracted from sources, so that the Knowledge Graph reflects what I am learning.
7. As a learner, I want generated lessons from source chunks, so that dense material becomes easier to understand before practice.
8. As a learner, I want generated practice exercises from sources, so that studying becomes active rather than passive.
9. As a learner, I want generated exercises to include starter code, solution code, local tests, hints, examples, tags, and source references, so that they work in the current practice flow.
10. As a learner, I want exercises exported to the existing practice catalog, so that the current UI remains useful while the internal model evolves.
11. As a learner, I want the internal artifact model to preserve workflow, source, citation, concept, status, and eval metadata, so that generated content can improve over time.
12. As a learner, I want a Practice Surface with lesson sections, exercises, code, output, and hints, so that I can learn and solve in one flow.
13. As a learner, I want to launch a sandbox or IDE-like surface when practice requires code, so that I can move from explanation to implementation without switching tools.
14. As a learner, I want code execution to remain sandboxed, so that generated and user-written practice code is safe to run locally.
15. As a learner, I want Socratic hints that do not give away answers, so that I can build understanding instead of copying solutions.
16. As a learner, I want hints to use my current code, source context, graph facts, and memory, so that the tutor responds to my actual situation.
17. As a learner, I want failed attempts and repeated hint requests to reveal Blind Spots, so that the system can target weak concepts.
18. As a learner, I want concept mastery updated from practice events, so that the system can recommend useful next steps.
19. As a learner, I want session summaries, so that long study sessions remain useful without bloating future context.
20. As a learner, I want the Knowledge Graph to link domains, subjects, chapters, topics, concepts, prerequisites, sources, exercises, attempts, and mastery signals, so that learning continuity survives across sources.
21. As a learner, I want a graph view of concepts and prerequisites, so that I can see how robotics topics connect.
22. As a learner, I want a Resource Manager that feels like Claude projects and NotebookLM notebooks, so that sources, artifacts, memory, and workflows are easy to browse.
23. As a learner, I want workflow buttons for creating exercises, lessons, explanations, summaries, concept extraction, and quizzes, so that common learning actions are available without writing prompts.
24. As an advanced learner, I want workflow prompts editable like a prompt library, so that I can customize how artifacts are generated.
25. As an advanced learner, I want workflows represented as structured templates, so that outputs can be validated and tested.
26. As a learner, I want small notes or snippets to generate lessons and exercises too, so that not every workflow requires a large source.
27. As a learner, I want NotebookLM-style artifacts such as mind maps, reports, flashcards, slide decks, and data tables to be possible later, so that the workspace can grow without changing its foundation.
28. As a learner, I want the system to use conservative context budgets by default, so that tutor behavior is precise and not polluted by irrelevant source material.
29. As a learner, I want explicit deep-source mode for long synthesis tasks, so that large context is used intentionally rather than accidentally.
30. As a learner, I want the Model Router Contract to support BYOK and multiple providers, so that the platform is not tied to one model vendor.
31. As a learner, I want model-specific prompting to be optional and isolated, so that changing models does not rewrite the Harness.
32. As a developer, I want retrieval behind a RetrievalLayer, so that Qdrant can be replaced or complemented later.
33. As a developer, I want graph storage behind a GraphLayer, so that Graphiti and Kuzu are first implementations rather than product lock-in.
34. As a developer, I want AI calls handled through typed Python contracts, so that agents and workflows are inspectable and testable.
35. As a developer, I want structured extraction and generation validated with Pydantic models, so that malformed AI output fails fast.
36. As a developer, I want Pydantic Evals around AI behavior, so that prompt, retrieval, and tutor changes are regression tested.
37. As a developer, I want generated practice code run in the sandbox during validation, so that broken exercises are blocked before reaching the learner.
38. As a developer, I want JSONL eval logs, so that behavior changes can be compared across model, prompt, workflow, and source changes.
39. As an agent working on the repo, I want clear Layer Contracts and ADRs, so that I can implement a bounded slice without reopening product decisions.
40. As an agent working on the repo, I want initial tracer bullets through the whole stack, so that later layer tasks can proceed safely.

## Implementation Decisions

- The product spine is an Adaptive Practice Workspace, not a generic chatbot, learning OS, or standalone ingestion product.
- The existing practice UI should be evolved into a Workspace Shell rather than replaced with a landing page or chat-only interface.
- The Workspace Shell contains persistent left navigation, a central Practice Surface, and dockable side and bottom panels.
- The Resource Manager organizes Learning Sources and Ingestion Artifacts by domain, subject, chapter, and topic.
- Learning Sources include PDFs, books, slide decks, Word documents, uploaded video or playlist transcripts, GitHub repositories, documentation sites, and manual notes.
- The Ingestion Harness remains independently callable, but its output is judged by whether it improves the practice loop.
- The Ingestion Harness produces multiple Ingestion Artifact types: source registry records, normalized documents, chunks, citations, concept candidates, graph facts, lessons, exercises, quizzes, and later richer artifacts.
- `problems.json` is a compatibility export only. The internal source of truth is a richer artifact model.
- PracticeArtifact records source references, concept identifiers, workflow identifiers, citations, graph links, eval scores, status, and typed payloads.
- The first workflow set covers practice and source understanding: create exercises, create lessons and explanations, generate hints, summarize source or chapter, extract concepts and prerequisites, and generate quizzes.
- A key starter workflow lets the learner select ingested sources and generate the current PracDaGo content model.
- Studio-like artifacts such as mind maps, reports, flashcards, slide decks, and data tables are deferred but supported by the workflow system design.
- Workflows are structured templates with editable prompts. They define input source types, context slots, prompt text, output schema, eval checks, and artifact type.
- The mandatory v1 Layer Contracts are Source Ingestion, Retrieval, Memory, Graph, Context Builder, Model Router, and Tool Registry.
- Retrieval starts with Qdrant behind RetrievalLayer.
- Graph starts with Graphiti and Kuzu behind GraphLayer.
- The product owns its Learning Graph, Source Graph, and Memory Graph concepts.
- Graphiti is a first implementation for temporal graph behavior, not the product memory model.
- SQLite stores source registry records, artifacts, sessions, attempts, memory events, workflow metadata, eval results, and durable app state.
- Shared Learning Memory starts with Source Ingested, Artifact Generated, Practice Attempted, Hint Requested, Blind Spot Detected, Concept Mastery Updated, and Session Summary Created events.
- User preferences and custom rules are important, but they are not a blocker for the first version.
- The Context Engineering Layer uses fixed named slots with budgets and controlled retrieval inside named slots.
- Default context budget is conservative, around 30k to 40k tokens, even when models support larger windows.
- Deep-source mode is explicit and reserved for ingestion, research, and source synthesis workflows.
- Default context slots include system, workflow template, skills and rules, learner memories, graph facts, retrieved source chunks, tools, history summary and tail, examples or artifacts, and user request.
- The system slot is a hard budget and must not be silently truncated.
- The Context Engineering Layer depends on RetrievalLayer, GraphLayer, MemoryStore, ModelRouter, and ToolRegistry rather than direct storage or provider clients.
- AI runtime starts with Pydantic AI for typed agents, dependency injection, tools, and inspectable behavior.
- LiteLLM is an optional provider adapter in local BYOK mode, not a mandatory gateway service.
- Instructor is used selectively for extraction, eval judging, and retry-heavy structured outputs.
- LangGraph is deferred until workflows need durable multi-step orchestration.
- DSPy is deferred until there are enough real examples and evals to optimize prompts meaningfully.
- The Tool Registry exposes safe, typed tools such as source search, graph lookup, prerequisite lookup, artifact lookup, sandbox run, symbolic math, plotting, and workflow execution.
- Implementation starts with one or two vertical tracer bullets through source ingestion, storage, retrieval, graph updates, workflow execution, UI, and evals.
- After tracer bullets prove contracts, smaller agents can expand extractors, artifact types, graph queries, workflow templates, eval cases, and UI panels.

## Deep Modules

- Ingestion Harness: accepts Learning Sources and produces normalized documents, chunks, citations, graph facts, lessons, exercises, and artifacts through a stable contract.
- RetrievalLayer: indexes and searches chunks and citations with filters for domain, subject, chapter, topic, source, artifact, and concept.
- GraphLayer: owns Learning Graph, Source Graph, and Memory Graph operations through product-specific methods.
- MemoryStore: records inspectable learning events and exposes derived facts for context assembly.
- Context Engineering Layer: builds model-ready context from fixed slots, budgets, retrieval, graph facts, memory, tools, examples, history, and user request.
- Workflow Engine: runs structured artifact workflows from templates, validates outputs, stores artifacts, and emits memory events.
- Model Router Contract: selects model provider, task settings, adapter behavior, and optional model-specific prompts without tying the Harness to one provider.
- Tool Registry: exposes typed tools with Pydantic validation and safe execution boundaries.
- Eval Harness: runs schema, sandbox, retrieval, context, tutor, grounding, and artifact quality checks.
- Workspace Shell: coordinates Resource Manager, Practice Surface, dockable panels, graph view, tutor chat, artifacts, terminal, and output.

## Testing Decisions

- Tests should target external behavior and contracts rather than implementation details.
- Existing ingestion tests are useful prior art for normalizer, chunker, structure detector, validator, dedup, and extractor behavior.
- Pydantic model validation is a hard gate for source records, chunks, artifacts, workflow outputs, tutor responses, graph facts, and eval scores.
- Generated practice code must be sandbox-executed before it can become an approved artifact.
- Workflow templates must have golden cases for representative sources and expected artifact shapes.
- Retrieval tests must verify filtering, citation metadata, source scoping, chunk ranking sanity, and empty-result behavior.
- Context builder tests must verify slot ordering, token budgets, truncation diagnostics, hard system budget failure, and deep-source mode boundaries.
- GraphLayer tests must verify concept insertion, prerequisite links, source links, artifact links, memory links, and migration-safe product contract behavior.
- MemoryStore tests must verify that required events are recorded, queryable, and tied to source, artifact, concept, session, or attempt identifiers.
- Tutor evals must check no answer leakage, specificity to current code, use of relevant context, prerequisite detection, and citation behavior where applicable.
- Artifact evals must check schema validity, source grounding, lesson usefulness, exercise quality, runnable tests, and duplicate detection.
- Pydantic Evals is the preferred v1 eval runner.
- JSONL result logs should be written for regression comparison.
- Promptfoo and Langfuse can be added later for declarative regression suites, red-teaming, tracing, and score analytics.
- Every major workflow should start with 5 to 10 representative eval cases before agents modify its prompts or contracts freely.

## Agent Work Split

### Higher-model tracer bullets

1. Source-to-practice tracer: ingest one PDF or uploaded transcript, create source registry records, chunks, Qdrant records, graph facts, a PracticeArtifact, `problems.json` export, and a UI path to practice it.
2. Tutor-context tracer: open a generated exercise, request a hint, assemble context from fixed slots, retrieve chunks, include graph and memory facts, return a validated Socratic response, and record Hint Requested plus Blind Spot or Mastery events.
3. Workflow-template tracer: run a structured workflow from selected sources, validate output, store artifact metadata, show it in Resource Manager, and run eval gates.

### Simpler agent expansion tasks

- Add PPT/DOCX extraction adapters.
- Add uploaded video and playlist transcript ingestion.
- Expand GitHub repository and docs ingestion modes.
- Add more workflow templates.
- Add more Pydantic models and migrations.
- Add Qdrant filtering tests.
- Add GraphLayer query helpers.
- Add eval cases for hints, lessons, exercises, quizzes, and citation grounding.
- Add UI panels for sources, artifacts, graph, memory, and output.
- Improve `problems.json` compatibility export.
- Polish Docker compose and local setup scripts.

## Out of Scope

- Hosted SaaS, accounts, auth, billing, teams, or multi-user sync.
- Public untrusted code execution.
- Full LangGraph multi-agent orchestration in v1.
- DSPy prompt compilation before sufficient real eval examples exist.
- Slide deck, audio overview, and video overview generation in the first cut.
- Full custom workflow builder before starter workflows are useful.
- Replacing every part of the existing PracDaGo UI at once.
- Migrating away from `problems.json` before compatibility export is stable.
- Betting the product on a single model provider, memory vendor, vector database, or graph database.

## Further Notes

The current ingestion pipeline is valuable and should be preserved as a seed, but it needs to be promoted into product contracts. Its strongest parts are the stage separation, source-aware extraction, math/code protection, validation, retry, review, and tests. Its main limitation is that it currently aims at `problems.json`; the product needs it to produce multi-purpose Ingestion Artifacts for retrieval, graph, memory, lessons, practice, review, and later artifact workflows.

The first build should keep the system thin but real. SQLite, Qdrant, Graphiti, Kuzu, Pydantic AI, Pydantic Evals, and the existing practice UI should be used through stable contracts. The goal is not to implement the full rich agentic platform immediately; the goal is to make the path from a thin foundation to that richer system short, testable, and deliberate.
