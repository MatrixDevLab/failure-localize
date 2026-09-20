import json
import tempfile
import unittest
from pathlib import Path

import failure_localize


class FailureLocalizeTests(unittest.TestCase):
    def test_truncation_is_first_and_retry_is_cascade(self):
        trace = [
            {"id": "m1", "seq": 1, "kind": "model_response", "finish_reason": "length", "call_id": "c1"},
            {"id": "r1", "seq": 2, "kind": "retry", "call_id": "c1", "status": "failed"},
        ]
        result = failure_localize.localize(trace)
        self.assertEqual(result["first_failure"]["category"], "truncated_tool_call")
        self.assertEqual(result["cascades"][0]["id"], "r1")

    def test_explicit_categories(self):
        cases = [
            ({"id": "a", "seq": 1, "kind": "tool_call", "tool_found": False}, "unknown_tool"),
            ({"id": "a", "seq": 1, "kind": "tool_call", "arguments_valid": False}, "invalid_arguments"),
            ({"id": "a", "seq": 1, "kind": "tool_result", "status": "error"}, "execution_failure"),
        ]
        for event, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(failure_localize.localize([event])["first_failure"]["category"], expected)

    def test_no_signal_is_insufficient(self):
        result = failure_localize.localize([{"id": "a", "seq": 1, "kind": "tool_result", "status": "ok"}])
        self.assertEqual(result["state"], "insufficient")

    def test_invalid_trace_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps({"events": [{"id": "a", "seq": 1}]}), encoding="utf-8")
            with self.assertRaises(failure_localize.InputError):
                failure_localize.load_trace(path)

    def test_output_is_deterministic(self):
        trace = [
            {"id": "r", "seq": 2, "kind": "retry", "call_id": "c", "status": "failed"},
            {"id": "m", "seq": 1, "kind": "tool_call", "call_id": "c", "validation_error": True},
        ]
        self.assertEqual(failure_localize.localize(trace), failure_localize.localize(list(reversed(trace))))


if __name__ == "__main__":
    unittest.main()

