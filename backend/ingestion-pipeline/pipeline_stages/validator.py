from __future__ import annotations

import ast
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from ..generator import GeneratedProblem
from .config import SANDBOX_BIN, SANDBOX_IMAGE


@dataclass
class ValidationResult:
    passed:        bool
    quality_score: float
    errors:        list[str] = field(default_factory=list)
    warnings:      list[str] = field(default_factory=list)


class Validator:
    def validate(self, p: GeneratedProblem) -> ValidationResult:
        errors:   list[str] = []
        warnings: list[str] = []

        for attr in ("starterCode", "solutionCode", "testCode"):
            code = getattr(p, attr)
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append(f"{attr} syntax error L{e.lineno}: {e.msg}")

        if errors:
            return ValidationResult(False, 0.0, errors, warnings)

        ok, msg = self._sandbox_run(p.solutionCode, p.testCode)
        if not ok:
            errors.append(f"Sandbox: {msg[:400]}")
            return ValidationResult(False, 0.0, errors, warnings)

        score = self._quality(p, warnings)
        return ValidationResult(True, score, errors, warnings)

    @staticmethod
    def _sandbox_run(solution: str, tests: str) -> tuple[bool, str]:
        combined = (
            solution.strip()
            + "\n\n# ── harness test ──────────────────────────\n"
            + tests.strip()
        )
        try:
            import shutil
            runtime = shutil.which(SANDBOX_BIN)

            if runtime:
                with tempfile.TemporaryDirectory() as tmp:
                    src = Path(tmp) / "solution.py"
                    src.write_text(combined)
                    result = subprocess.run(
                        [
                            runtime, "run", "--rm",
                            "--network",    "none",
                            "--memory",     "256m",
                            "--cpus",       "0.5",
                            "--pids-limit", "32",
                            "--read-only",
                            "--tmpfs",      "/tmp:rw,nosuid,nodev,size=64m",
                            "--security-opt", "no-new-privileges",
                            "--cap-drop",   "ALL",
                            "--user",       "65532:65532",
                            "-e", "PYTHONDONTWRITEBYTECODE=1",
                            "-v", f"{tmp}:/workspace:ro",
                            "-w", "/workspace",
                            SANDBOX_IMAGE,
                            "python3", "solution.py",
                        ],
                        capture_output=True, text=True, timeout=20,
                    )
                    if result.returncode == 0:
                        return True, result.stdout
                    return False, (result.stderr + result.stdout).strip()

            return Validator._inline_run(combined)

        except subprocess.TimeoutExpired:
            return False, "Timed out (>20 s)"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _inline_run(code: str) -> tuple[bool, str]:
        import contextlib
        import io
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(code, "<generated>", "exec"), {})
            return True, buf.getvalue()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _quality(p: GeneratedProblem, warnings: list[str]) -> float:
        score = 1.0

        exp_words = len(p.explanation.split())
        if exp_words < 200:
            score -= 0.20
            warnings.append(f"explanation thin ({exp_words} words; aim ≥200)")

        if any(t in ["math", "algebra", "calculus", "probability",
                     "linear_algebra", "statistics"]
               for t in p.tags):
            if "common mistake" not in p.explanation.lower():
                score -= 0.15
                warnings.append("maths problem missing 'Common mistakes' section")

        sol_lines = [line for line in p.solutionCode.splitlines() if line.strip()]
        if len(sol_lines) < 3:
            score -= 0.15
            warnings.append("solution code trivially short")

        assert_count = p.testCode.count("assert ")
        if assert_count < 3:
            score -= 0.10
            warnings.append(f"only {assert_count} assertions; aim ≥3")

        if not p.examples:
            score -= 0.10
            warnings.append("no examples provided")

        if not p.prerequisites:
            warnings.append("prerequisites empty — fill manually if relevant")

        return round(max(0.0, score), 3)
