# backend/storage/database.py
import sqlite3
from pathlib import Path
from contextlib import contextmanager

PLATFORM_DIR = Path.home() / ".platform"
DB_PATH = PLATFORM_DIR / "memory" / "platform.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    label TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS problems (
    id TEXT PRIMARY KEY,
    chapter TEXT, difficulty TEXT, tags TEXT,
    exercise_mode TEXT, verifier TEXT,
    content_json TEXT,                    -- full problem JSON
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,                  -- UUID
    started_at TEXT,
    ended_at TEXT,
    problem_id TEXT,
    project_id TEXT DEFAULT 'cmu_mrsd_prep',
    summary TEXT,                         -- compressed episodic summary
    branch_id TEXT DEFAULT 'main',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    branch_id TEXT DEFAULT 'main',
    parent_message_id INTEGER,            -- for branching
    role TEXT,                            -- user / assistant / tool
    content TEXT,
    tool_calls TEXT,                      -- JSON if tool was called
    tokens_used INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id TEXT,
    session_id TEXT,
    verdict TEXT,                         -- Accepted / Error / Timeout
    code TEXT,
    error_msg TEXT,
    duration_ms INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS branches (
    id TEXT PRIMARY KEY,                  -- UUID
    parent_branch_id TEXT,
    parent_message_id INTEGER,            -- branch point
    session_id TEXT,
    label TEXT,                           -- user-set name
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS graph_nodes (
    id TEXT PRIMARY KEY,                  -- concept slug
    label TEXT, domain TEXT,
    project_id TEXT DEFAULT 'cmu_mrsd_prep',
    mastery REAL DEFAULT 0.0,             -- 0.0 unseen → 1.0 mastered
    last_attempted TEXT,
    attempt_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS graph_edges (
    source TEXT, target TEXT,
    edge_type TEXT,                       -- prerequisite / related / part_of
    project_id TEXT DEFAULT 'cmu_mrsd_prep',
    weight REAL DEFAULT 1.0,
    PRIMARY KEY (source, target, edge_type)
);

CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    user_id TEXT DEFAULT 'local',
    content TEXT,
    tags TEXT,
    embedding_id TEXT,                    -- Chroma doc ID
    created_at TEXT DEFAULT (datetime('now'))
);
"""

@contextmanager
def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()

def bootstrap_projects():
    """Seed base milestone projects at first start."""
    with db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO projects (id, label) VALUES (?, ?)",
            ("cmu_mrsd_prep", "CMU MRSD Prep")
        )
        conn.execute(
            "INSERT OR IGNORE INTO projects (id, label) VALUES (?, ?)",
            ("go_foundations", "Go System Foundations")
        )
