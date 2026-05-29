# AI Runtime Uses Pydantic AI First

The AI runtime will start with Pydantic AI because the product needs typed Python control, dependency injection, tool calls, and inspectable agent behavior without making a heavyweight orchestration framework the foundation. LiteLLM may be used as a provider adapter for model-agnostic BYOK calls, but a central LiteLLM gateway is deferred until deployment, shared budgeting, or cross-provider operations require it; Instructor is reserved for extraction and evaluation paths where structured-output retries materially reduce failure risk.

## Considered Options

- LiteLLM gateway as the center: useful for hosted routing and budgeting, but unnecessary operational surface for local BYOK v1.
- Instructor everywhere: strong for schema extraction, but less useful than Pydantic AI for agent runtime, tools, and dependencies.
- LangGraph from v1: powerful for durable orchestration, but premature before the tutor, ingestion, memory, and graph contracts have stabilized.
