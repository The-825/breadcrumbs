#!/usr/bin/env python3
import importlib.util
import json
import pathlib
import unittest


RUNNER_PATH = pathlib.Path(__file__).with_name("hf_runner.py")
SPEC = importlib.util.spec_from_file_location("hf_runner", RUNNER_PATH)
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class TransportParsingTests(unittest.TestCase):
    def test_request_disables_default_thinking(self):
        payload = RUNNER.request_payload("model", "prompt")
        self.assertEqual(payload["chat_template_kwargs"], {"enable_thinking": False})
        self.assertEqual(payload["temperature"], 1.0)
        self.assertEqual(payload["top_p"], 0.95)

    def test_openai_json_response(self):
        payload = {"choices": [{"message": {"content": "{}"}}]}
        parsed = RUNNER.parse_transport_payload(json.dumps(payload).encode("utf-8"))
        self.assertEqual(parsed["choices"][0]["message"]["content"], "{}")

    def test_server_sent_event_response(self):
        raw = (
            b'data: {"choices":[{"delta":{"content":"{"}}]}\n\n'
            b'data: {"choices":[{"delta":{"content":"}"}}]}\n\n'
            b'data: [DONE]\n'
        )
        parsed = RUNNER.parse_transport_payload(raw, "text/event-stream")
        self.assertEqual(parsed["choices"][0]["message"]["content"], "{}")

    def test_invalid_payload_keeps_content_free_diagnostics(self):
        with self.assertRaises(RUNNER.TransportParseError) as raised:
            RUNNER.parse_transport_payload(b"not-json", "text/plain")
        self.assertEqual(raised.exception.diagnostics["response_bytes"], 8)
        self.assertEqual(set(raised.exception.diagnostics), {
            "content_type", "response_bytes", "response_sha256"
        })

    def test_fenced_model_answer(self):
        answer = RUNNER.parse_model_answer('```json\n{"next_action":"rebase"}\n```')
        self.assertEqual(answer, {"next_action": "rebase"})

    def test_embedded_model_answer(self):
        answer = RUNNER.parse_model_answer('Result:\n{"next_action":"rebase"}\nDone.')
        self.assertEqual(answer, {"next_action": "rebase"})

    def test_invalid_model_answer_keeps_content_free_diagnostics(self):
        with self.assertRaises(RUNNER.ModelAnswerParseError) as raised:
            RUNNER.parse_model_answer("not-json")
        self.assertEqual(set(raised.exception.diagnostics), {
            "content_chars", "content_sha256", "starts_with_code_fence",
            "starts_with_json_object"
        })


if __name__ == "__main__":
    unittest.main()
