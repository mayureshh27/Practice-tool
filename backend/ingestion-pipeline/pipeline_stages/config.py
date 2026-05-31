import os
from pathlib import Path

CATALOG_PATH     = Path("data/problems.json")
SANDBOX_IMAGE    = os.getenv("GOPRAC_SANDBOX_IMAGE", "learning-platform:python")
SANDBOX_BIN      = os.getenv("GOPRAC_SANDBOX_BIN",   "docker")
EMBED_MODEL      = "all-MiniLM-L6-v2"
DEDUP_THRESHOLD  = 0.88
QUALITY_AUTOPASS = 0.82
MAX_RETRIES      = 3
