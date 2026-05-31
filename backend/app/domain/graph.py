"""Product-owned graph domain models.

These types are the interface between the GraphLayer and the rest of the
application. No Graphiti or Kuzu types leak into these models — they are
plain Pydantic models owned by the product (graph-layer-spike.md §1).

Storage backend mapping (ADR-0028):
  - Kuzu stores: concept_id, canonical_name, aliases, structural edges
    (PREREQUISITE_OF, APPEARS_IN, TARGETS_CONCEPT)
  - Graphiti stores: temporal mastery edges with mastery_score,
    trigger_event_id, recorded_at, valid_from, valid_to (ADR-0026)
  - GraphLayer wrapper derives: mastery_score and last_updated_at from
    Graphiti edges; prerequisite_ids from Kuzu PREREQUISITE_OF edges
"""

from collections.abc import Sequence
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConceptCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    definition: str | None = None
    aliases: Sequence[str] = []
    prerequisite_names: Sequence[str] = []


class ConceptNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    concept_id: str
    canonical_name: str
    aliases: Sequence[str] = []
    mastery_score: float | None = None
    last_updated_at: datetime | None = None
    prerequisite_ids: Sequence[str] = []


class ConceptContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    concepts: Sequence[ConceptNode] = []
    prereq_chain: Sequence[ConceptNode] = []
    gap_concepts: Sequence[ConceptNode] = []
