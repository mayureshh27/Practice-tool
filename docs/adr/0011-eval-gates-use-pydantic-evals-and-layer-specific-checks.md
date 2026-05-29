# Eval Gates Use Pydantic Evals And Layer-Specific Checks

The harness will use a full AI evaluation gate before trusting changes to prompts, ingestion, context assembly, tutor behavior, retrieval, or artifact generation. Pydantic Evals is the preferred v1 eval runner because it is code-first, Python-native, and aligned with Pydantic AI; Promptfoo and Langfuse may be added later for declarative regression suites, red-teaming, tracing, and score analytics.

## Consequences

V1 evals must include schema validation, sandbox execution for generated practice code, golden workflow cases, retrieval and context budget checks, hint no-leak checks, citation grounding checks, artifact quality rubrics, and JSONL result logs. The suite can start small, but each major workflow should have representative cases before agents are allowed to modify its prompts or contracts.
