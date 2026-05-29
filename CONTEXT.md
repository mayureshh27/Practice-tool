# Practice Tool

This context defines the product language for a local-first adaptive practice workspace for technical learning. It keeps future design and implementation work centered on the learning loop rather than drifting into a generic AI workspace.

## Language

**Adaptive Practice Workspace**:
The primary product spine: a place where a learner studies structured material, solves exercises, receives feedback, and builds mastery over time. Ingestion, chat, memory, graphs, and tools exist to support this practice loop.
_Avoid_: Learning OS, generic agent workspace, chatbot

**Ingestion Harness**:
A supporting subsystem that turns books, videos, repositories, and web sources into structured learning content for the Adaptive Practice Workspace. It remains independently runnable so ingestion can be tested, improved, and reused without the full UI.
_Avoid_: Scraper, import script

**Learning Source**:
Any learner-selected input that can be transformed into study material, including PDFs, books, slide decks, Word documents, uploaded video or playlist transcripts, GitHub repositories, documentation sites, and manual notes. The domain model must allow multiple source types from the start.
_Avoid_: Book, document, upload

**Ingestion Artifact**:
Any structured output produced from a Learning Source, such as normalized text, chunks, source citations, concept candidates, graph facts, exercises, lessons, quizzes, flashcards, diagrams, or practice projects. Exercises are one important artifact, not the only ingestion output.
_Avoid_: Problem, generated content

**Context Engineering Layer**:
The system boundary that decides what source material, memory, skill rules, tool descriptions, examples, and recent session history are assembled for an AI call. It is a first-class product foundation, not incidental prompt text inside endpoints.
_Avoid_: Prompt, system prompt, RAG prompt

**Layer Contract**:
A stable interface between major subsystems such as ingestion, storage, retrieval, memory, graph, model routing, context building, tools, and UI. Implementations may start simple, but the workspace should depend on contracts so better tools can replace early choices without rewriting the product.
_Avoid_: Wrapper, abstraction for abstraction's sake

**Evolution Path**:
The planned progression from thin but real foundations to a richer agentic system. The first build should make the path to orchestration, branching, richer memory, and stronger evals short, but should not pretend those advanced behaviors already exist.
_Avoid_: Roadmap, future work

**Model Router Contract**:
The system boundary that maps task types, budgets, context length, privacy constraints, and provider availability to model calls. The harness must stay model-agnostic; model-specific prompts and adapters may improve performance, but core product behavior should not depend on any single provider or require a gateway service in local BYOK mode.
_Avoid_: Claude integration, OpenAI integration, LLM client

**Harness**:
The engineered system of contracts, evaluators, prompts, tools, storage, and workflows that makes learning behavior repeatable and inspectable across models and sources. The harness is the durable product asset; individual model providers are replaceable implementations.
_Avoid_: Prompt stack, agent magic

**Shared Learning Memory**:
The learner-owned store of progress, attempts, source notes, session summaries, concept links, and recallable context used across practice sessions and study tools. It is common infrastructure for the workspace, not a separate product.
_Avoid_: Chat memory, vector store, database

**Knowledge Graph**:
The structured map of concepts, chapters, domains, prerequisites, source references, exercises, and mastery signals. It spans all Learning Sources and subjects so the workspace can recommend practice, show relationships, and preserve continuity across study sessions.
_Avoid_: Visual graph, graph database

**Graph Layer**:
The Layer Contract responsible for storing, querying, and evolving Learning Graph, Source Graph, and Memory Graph data. It may start with Graphiti and a supported graph backend, but the workspace must preserve ownership of its graph schema and migration path.
_Avoid_: Graphiti integration, graph vendor

**Blind Spot**:
A concept, skill, or prerequisite where the learner repeatedly struggles, shows weak recall, or fails related exercises. Blind Spots should be tracked across chapters and subjects so the workspace can generate targeted lessons, practice, and review.
_Avoid_: Weak tag, mistake

**Study Tool**:
A focused interface inside the workspace, such as NotebookLM-style source chat, an IDE-like practice view, or a concept graph. A Study Tool must read from or write to Shared Learning Memory instead of becoming an isolated silo.
_Avoid_: App, standalone feature

**Workspace Shell**:
The primary UI frame for the Adaptive Practice Workspace: persistent left navigation, central work area, and dockable side and bottom surfaces for sources, tutor chat, artifacts, graph, terminal, output, and practice tools. It should evolve the existing practice UI rather than replace it with a generic chat app.
_Avoid_: Dashboard, landing page

**Resource Manager**:
The Study Tool for organizing Learning Sources and generated artifacts by domain, subject, chapter, and topic. It should feel closer to NotebookLM projects and Claude projects than to a file browser, but its outputs feed the practice loop.
_Avoid_: File manager, upload panel

**Practice Surface**:
The central Study Tool where lessons, exercises, code, sandbox execution, and generated practice artifacts are used. It may launch an IDE-like editor or custom sandbox when needed, but the default experience remains learning and practice rather than raw coding.
_Avoid_: IDE, code editor

## Flagged Ambiguities

**Local**:
Resolved as local-first and Docker-runnable. The product should run on the learner's machine by default while preserving a path to later deployment.

## Example Dialogue

Developer: Should the NotebookLM-style chat become the main product?

Domain expert: No. It is a Study Tool inside the Adaptive Practice Workspace. It helps interrogate sources and memory, but the main loop is still practice, feedback, and mastery.

Developer: Can the ingestion pipeline be developed separately?

Domain expert: Yes. The Ingestion Harness should stay independently callable, but its output is judged by whether it improves the practice loop.

Developer: Can we defer memory and graph until after the first ingestion demo?

Domain expert: No. The first slice can have simple implementations, but Context Engineering Layer, Shared Learning Memory, and Knowledge Graph must exist as real system boundaries from the start.

Developer: Should we hard-code Chroma, NetworkX, and SQLite directly into the tutor and UI?

Domain expert: No. Those can be first implementations, but the Adaptive Practice Workspace should depend on Layer Contracts so each layer can evolve toward the richer agentic system independently.

Developer: Is the project mainly about integrating one best model?

Domain expert: No. The Harness is the durable product. Models should be swappable through the Model Router Contract, with optional model-specific prompting kept behind adapters.

Developer: Should Graphiti become the product's memory model?

Domain expert: No. Graphiti can be the first Graph Layer implementation, but the product owns Learning Graph, Source Graph, and Memory Graph concepts through its own Layer Contract.

Developer: Should the first UI become a plain chat interface?

Domain expert: No. The UI should be a Workspace Shell that preserves the existing practice primitives while adding Resource Manager, dockable tutor/source panels, artifacts, graph, and optional IDE-like practice surfaces.

Developer: Should ingestion write only problems.json?

Domain expert: No. problems.json can remain a compatibility export, but the Ingestion Harness should produce Ingestion Artifacts for retrieval, graph, memory, lessons, practice, and review workflows.
