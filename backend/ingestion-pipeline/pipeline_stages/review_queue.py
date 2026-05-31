from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from ..generator import GeneratedProblem
from .config import QUALITY_AUTOPASS
from .validator import ValidationResult, Validator


class ReviewQueue:
    PENDING_PATH = Path("data/pending_review.json")

    def __init__(self, validator: Validator):
        self.validator = validator
        self.approved: list[GeneratedProblem] = []
        self.rejected: list[str]              = []
        self.pending:  list[dict]             = []

    def review(self, p: GeneratedProblem, result: ValidationResult):
        if result.passed and result.quality_score >= QUALITY_AUTOPASS \
                and not result.errors:
            self.approved.append(p)
            return

        if not result.passed:
            print(f"  ✗ AUTO-REJECT {p.id}: {'; '.join(result.errors[:2])}")
            self.rejected.append(p.id)
            return

        self._display_summary(p, result)
        while True:
            raw = input("  Action [a]pprove [e]dit [r]eject [s]kip [v]iew: ").strip().lower()
            action = raw[0] if raw else "s"
            if action == "a":
                self.approved.append(p)
                break
            elif action == "e":
                edited = self._open_editor(p)
                if edited:
                    re_result = self.validator.validate(edited)
                    if re_result.passed:
                        self.approved.append(edited)
                        print(f"  ✓ Approved after edit (quality={re_result.quality_score:.2f})")
                    else:
                        print(f"  ✗ Re-validation failed: {re_result.errors}")
                        self.pending.append(edited.model_dump())
                break
            elif action == "r":
                self.rejected.append(p.id)
                break
            elif action == "s":
                self.pending.append(p.model_dump())
                break
            elif action == "v":
                print(json.dumps(p.model_dump(), indent=2)[:3000])
            else:
                print("  Unknown action. Try a/e/r/s/v")

    def flush_pending(self):
        if not self.pending:
            return
        self.PENDING_PATH.parent.mkdir(parents=True, exist_ok=True)
        existing = []
        if self.PENDING_PATH.exists():
            existing = json.loads(self.PENDING_PATH.read_text())
        self.PENDING_PATH.write_text(
            json.dumps(existing + self.pending, indent=2)
        )
        print(f"  📋 {len(self.pending)} problems written to {self.PENDING_PATH}")

    @staticmethod
    def _display_summary(p: GeneratedProblem, r: ValidationResult):
        bar = "█" * int(r.quality_score * 20) + "░" * (20 - int(r.quality_score * 20))
        print(f"\n  ┌─ {p.title}")
        print(f"  │  id={p.id}  chapter={p.chapter}  difficulty={p.difficulty}")
        print(f"  │  quality=[{bar}] {r.quality_score:.2f}")
        if r.warnings:
            print(f"  │  warnings: {', '.join(r.warnings[:3])}")
        print(f"  └─ tags: {', '.join(p.tags[:5])}")

    @staticmethod
    def _open_editor(p: GeneratedProblem) -> GeneratedProblem | None:
        editor = os.getenv("EDITOR", "nano")
        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False, encoding="utf-8"
        ) as f:
            json.dump(p.model_dump(), f, indent=2, ensure_ascii=False)
            fname = f.name
        subprocess.run([editor, fname])
        try:
            data = json.loads(Path(fname).read_text())
            return GeneratedProblem(**data)
        except Exception as e:
            print(f"  Parse error after edit: {e}")
            return None
        finally:
            Path(fname).unlink(missing_ok=True)
