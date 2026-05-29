# backend/memory/manager.py
from __future__ import annotations
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import chromadb
import litellm
from storage.database import db, PLATFORM_DIR

CHROMA_PATH = PLATFORM_DIR / "data" / "chroma"
SUMMARIES_DIR = PLATFORM_DIR / "memory" / "summaries"

@dataclass
class MemoryConfig:
    embed_model:        str   = "gemini/text-embedding-004"
    semantic_top_k:     int   = 6
    semantic_threshold: float = 0.55
    history_max_tokens: int   = 15000
    keep_pairs:         int   = 5
    compress_model:     str   = "gemini/gemini-2.5-flash"

class FourTierMemory:
    """
    Working    — Active session conversation context in memory / React
    Episodic   — SQLite message logs & weekly compressed summaries
    Semantic   — Atomic facts extracted, embedded, and queried in local Chroma
    Procedural — Skills files loaded contextually (handled by skills_loader)
    """

    def __init__(self, cfg: MemoryConfig = MemoryConfig(), api_key: str | None = None):
        self.cfg = cfg
        self.api_key = api_key

        # Initialize local file-based ChromaDB client
        CHROMA_PATH.mkdir(parents=True, exist_ok=True)
        self._chroma = chromadb.PersistentClient(path=str(CHROMA_PATH))
        self._mem_col = self._chroma.get_or_create_collection("memories")
        self._chunk_col = self._chroma.get_or_create_collection("chunks")

        self._history: list[dict] = []
        self._summary: str | None = None

    def _get_embedding(self, text: str) -> list[float]:
        """Generate vector embedding via Gemini API."""
        try:
            response = litellm.embedding(
                model=self.cfg.embed_model,
                input=[text],
                api_key=self.api_key
            )
            return response['data'][0]['embedding']
        except Exception as e:
            # Safe zero-vector fallback in case of API failure or lack of keys
            print(f"[!] Embedding generation error: {e}")
            return [0.0] * 768

    # ── EPISODIC ─────────────────────────────────────────────────────────────

    def load_session_history(self, session_id: str, branch_id: str = "main"):
        """Load conversation history for a session/branch from SQLite."""
        self._history = []
        with db() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages "
                "WHERE session_id=? AND branch_id=? "
                "ORDER BY id",
                (session_id, branch_id)
            ).fetchall()
            for r in rows:
                self._history.append({"role": r["role"], "content": r["content"]})
        
        # Load accumulated summaries if available
        # Find latest compressed summary for this session in summaries folder
        self._summary = None
        # We can also load summary from the sessions table
        with db() as conn:
            row = conn.execute(
                "SELECT summary FROM sessions WHERE id=?", (session_id,)
            ).fetchone()
            if row and row["summary"]:
                self._summary = row["summary"]

    def push_message(self, role: str, content: str, session_id: str, branch_id: str = "main", parent_message_id: int | None = None):
        """Add a message to active memory and log to SQLite database."""
        self._history.append({"role": role, "content": content})
        self._persist_message(role, content, session_id, branch_id, parent_message_id)
        self._maybe_compress(session_id)

    def _persist_message(self, role: str, content: str, session_id: str, branch_id: str, parent_message_id: int | None = None):
        with db() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, branch_id, parent_message_id, role, content) "
                "VALUES (?, ?, ?, ?, ?)",
                (session_id, branch_id, parent_message_id, role, content)
            )

    def _maybe_compress(self, session_id: str):
        from context.skills_loader import count_tokens
        total = count_tokens(" ".join(m["content"] for m in self._history))
        if total <= self.cfg.history_max_tokens:
            return
            
        # Keep the latest turns verbatim
        keep = self.cfg.keep_pairs * 2
        to_compress = self._history[:-keep]
        self._history = self._history[-keep:]

        if not to_compress:
            return

        dialogue = "\n".join(
            f"{m['role'].upper()}: {m['content'][:400]}"
            for m in to_compress
        )
        prompt = (
            "You are a Socratic study archivist. Summarize this segment of the tutoring session in under 150 words.\n"
            "Identify:\n"
            "1. Core concept discussed (e.g. eigenvalues, cross products).\n"
            "2. Specific misunderstandings or errors the student made.\n"
            "3. The Socratic question that resolved it.\n"
            "Format cleanly as prose.\n\n"
            "Dialogue:\n" + dialogue
        )
        try:
            resp = litellm.completion(
                model=self.cfg.compress_model,
                api_key=self.api_key,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
            )
            new_summary = resp.choices[0].message.content.strip()
            self._summary = (
                (self._summary + "\n\n" + new_summary)
                if self._summary else new_summary
            )
            
            # Persist summary back to SQLite session row
            with db() as conn:
                conn.execute(
                    "UPDATE sessions SET summary=? WHERE id=?",
                    (self._summary, session_id)
                )
            
            # Save a copy as a markdown summary file
            self._persist_summary(new_summary)
        except Exception as e:
            print(f"[!] Episodic memory compression failed: {e}")

    def _persist_summary(self, text: str):
        week = datetime.now().strftime("%Y-W%W")
        SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
        path = SUMMARIES_DIR / f"{week}.md"
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n\n## {datetime.now().isoformat()}\n{text}")

    def history_messages(self) -> list[dict]:
        """Construct the full conversation dialogue incorporating compressed summaries."""
        result = []
        if self._summary:
            result += [
                {"role": "user",
                 "content": f"[Chronological session context summaries so far]:\n{self._summary}"},
                {"role": "assistant",
                 "content": "Understood. I have loaded your historic concepts and previous mistakes into my Socratic context."}
            ]
        result.extend(self._history)
        return result

    # ── SEMANTIC ─────────────────────────────────────────────────────────────

    def add_fact(self, text: str, tags: list[str] = []):
        """Extract atomic facts from text using Gemini, generate embeddings, and store."""
        prompt = (
            "Extract 1 to 5 Socratic learning facts from this text. An atomic fact is a single sentence "
            "documenting user preferences, specific concept mastery levels, or recurring coordinate transformation errors.\n"
            "Return strictly as a JSON object with a single field 'facts' containing a list of strings.\n\n"
            f"Input text:\n{text}"
        )
        try:
            resp = litellm.completion(
                model=self.cfg.compress_model,
                api_key=self.api_key,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=300,
            )
            data = json.loads(resp.choices[0].message.content)
            facts = data.get("facts", [text])
        except Exception:
            # Fallback to saving the text as a single fact
            facts = [text]

        for fact in facts:
            emb = self._get_embedding(fact)
            doc_id = str(uuid.uuid4())
            tag_str = ",".join(tags)
            
            # Save to SQLite first
            with db() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO memories (id, content, tags, embedding_id) VALUES (?, ?, ?, ?)",
                    (doc_id, fact, tag_str, doc_id)
                )
            
            # Index in local Chroma
            self._mem_col.upsert(
                ids=[doc_id],
                embeddings=[emb],
                documents=[fact],
                metadatas=[{"tags": tag_str}]
            )

    def recall(self, query: str, top_k: int = 6, tag_filter: list[str] | None = None) -> list[str]:
        """Perform a semantic search over stored user facts using local Chroma."""
        if self._mem_col.count() == 0:
            return []
            
        q_emb = self._get_embedding(query)
        where = {"tags": {"$contains": tag_filter[0]}} if tag_filter else None
        
        results = self._mem_col.query(
            query_embeddings=[q_emb],
            n_results=min(top_k, self._mem_col.count()),
            where=where,
        )
        
        docs = results["documents"][0]
        distances = results["distances"][0]
        
        # Convert distances to similarity (e.g. L2 distance conversion)
        recalled = []
        for doc, dist in zip(docs, distances):
            similarity = 1.0 / (1.0 + dist)  # Standard distance-to-similarity
            if similarity >= self.cfg.semantic_threshold:
                recalled.append(doc)
        return recalled

    def weak_tags(self, top_n: int = 5) -> list[str]:
        """Retrieve tags that have the highest number of failed attempts in SQLite."""
        tag_counts: dict[str, int] = {}
        with db() as conn:
            rows = conn.execute(
                "SELECT p.tags FROM attempts a "
                "JOIN problems p ON a.problem_id = p.id "
                "WHERE a.verdict != 'Accepted'"
            ).fetchall()
            
            for row in rows:
                tags = row["tags"].split(",") if row["tags"] else []
                for tag in tags:
                    t = tag.strip().lower()
                    if t:
                        tag_counts[t] = tag_counts.get(t, 0) + 1
                        
        return sorted(tag_counts, key=tag_counts.get, reverse=True)[:top_n]

    # ── CHUNK RETRIEVAL (RAG Ingestion) ───────────────────────────────────────

    def add_chunk(self, text: str, metadata: dict):
        """Index a textbook chunk in Chroma for RAG."""
        doc_id = metadata.get("id", str(uuid.uuid4()))
        emb = self._get_embedding(text)
        
        # Chroma expects metadatas to contain simple types (str, int, float, bool)
        chroma_meta = {k: str(v) if not isinstance(v, (int, float, bool)) else v for k, v in metadata.items()}
        
        self._chunk_col.upsert(
            ids=[doc_id],
            embeddings=[emb],
            documents=[text],
            metadatas=[chroma_meta]
        )

    def search_chunks(self, query: str, top_k: int = 5, chapter_filter: str | None = None) -> list[dict]:
        """Query vector database for relevant study chunks."""
        if self._chunk_col.count() == 0:
            return []
            
        q_emb = self._get_embedding(query)
        where = {"chapter": chapter_filter} if chapter_filter else None
        
        results = self._chunk_col.query(
            query_embeddings=[q_emb],
            n_results=min(top_k, self._chunk_col.count()),
            where=where,
        )
        
        chunks = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            chunks.append({"text": doc, "metadata": meta})
        return chunks
