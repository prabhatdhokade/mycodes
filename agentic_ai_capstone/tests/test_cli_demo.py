from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_cli_demo_runs() -> None:
    project_root = Path(__file__).resolve().parents[1]
    src_path = project_root / "src"
    cmd = [
        sys.executable,
        "-m",
        "agentic_ai_capstone.main",
        "--customer-id",
        "cust-1001",
        "--message",
        "I need invoice details",
    ]
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
        env={
            **__import__("os").environ,
            "PYTHONPATH": str(src_path),
        },
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "response" in payload
    assert payload["state"]["current_agent"] in {"billing", "technical", "refund", "triage"}
