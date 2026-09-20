import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, fixture: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "failure_localize.py"), str(ROOT / fixture)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_normalized_example_is_localized(self):
        result = self.run_cli("examples/normalized-trace.json")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["first_failure"]["category"], "truncated_tool_call")
        self.assertEqual(payload["cascades"][0]["id"], "workflow-1")

    def test_malformed_trace_returns_structured_error(self):
        result = self.run_cli("fixtures/malformed.json")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["state"], "invalid")


if __name__ == "__main__":
    unittest.main()
