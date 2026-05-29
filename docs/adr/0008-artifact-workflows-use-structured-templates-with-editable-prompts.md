# Artifact Workflows Use Structured Templates With Editable Prompts

Artifact generation will use structured workflow templates that define source inputs, context slots, prompt text, output schema, evaluation checks, and artifact type. Starter workflows such as creating exercises, lessons, explanations, quizzes, concept maps, and reports may appear as UI actions, but their prompts remain editable so advanced users can customize the learning harness without changing code.

## Consequences

The workflow system should feel like a prompt library to the learner while remaining machine-readable for validation, tracing, and artifact storage. The UI should help users create or adapt templates rather than forcing every workflow through free-form chat.
