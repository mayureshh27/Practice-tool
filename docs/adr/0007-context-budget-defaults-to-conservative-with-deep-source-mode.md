# Context Budget Defaults To Conservative With Deep Source Mode

The Context Engineering Layer will default to a conservative 30k-40k token context budget even when models support much larger windows, because the core practice loop depends on precise context selection and resistance to bloat. Long-context behavior is available only through explicit deep-source workflows for ingestion, research, or source synthesis tasks where larger context is justified.

## Consequences

Default slots include system, workflow template, skills and rules, learner memories, graph facts, retrieved source chunks, tools, history summary and tail, examples or artifacts, and the user request. Agents should not paste entire sources into tutor or practice prompts; they must retrieve, summarize, or enter deep-source mode intentionally.
