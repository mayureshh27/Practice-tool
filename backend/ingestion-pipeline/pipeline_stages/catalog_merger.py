from __future__ import annotations

import json
import subprocess
from datetime import UTC
from pathlib import Path

from ..generator import GeneratedProblem
from .config import CATALOG_PATH


class CatalogMerger:
    def __init__(self, catalog_path: Path = CATALOG_PATH):
        self.path = catalog_path

    def merge(self, approved: list[GeneratedProblem],
              chapter_id: str, chapter_title: str,
              auto_commit: bool = False):
        if not approved:
            print("  No problems to merge.")
            return

        if self.path.exists():
            catalog = json.loads(self.path.read_text())
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            catalog = {"chapters": [], "problems": []}

        ch_ids = {c["id"] for c in catalog["chapters"]}
        if chapter_id not in ch_ids:
            catalog["chapters"].append(
                {"id": chapter_id, "title": chapter_title}
            )
            print(f"  + Added chapter: {chapter_id} — {chapter_title}")

        existing_max = max(
            (p.get("number", 0) for p in catalog["problems"]), default=0
        )
        new_dicts = []
        for i, p in enumerate(approved):
            d = p.model_dump()
            d["number"] = existing_max + i + 1
            new_dicts.append(d)

        catalog["problems"].extend(new_dicts)

        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
        tmp.replace(self.path)

        print(f"  ✓ Merged {len(approved)} problems")
        print(f"    Catalog: {len(catalog['problems'])} problems "
              f"across {len(catalog['chapters'])} chapters")

        if auto_commit:
            self._git_commit(chapter_id, len(approved))

    def _git_commit(self, chapter_id: str, count: int):
        try:
            subprocess.run(
                ["git", "add", str(self.path)],
                check=True, capture_output=True
            )
            from datetime import datetime
            msg = (
                f"harness: add {count} problems to {chapter_id}\n\n"
                f"Generated {datetime.now(UTC).isoformat()}"
            )
            subprocess.run(
                ["git", "commit", "-m", msg],
                check=True, capture_output=True
            )
            print("  ↳ git commit created")
        except subprocess.CalledProcessError:
            print("  ↳ git commit skipped")
