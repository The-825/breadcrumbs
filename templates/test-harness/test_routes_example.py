"""Proof tests for the harness: boot the real app, assert route behavior.

These cover what the parse layer cannot: the auth gate really rejects an
anonymous request, a flag left OFF really hides its route, and the data
route really returns the seeded rows. All fixture rows are synthetic.

Run from this directory: python3 -m unittest discover
"""
import unittest

from harness import AUTH_HEADER, AUTH_HEADERS, TEST_CALLER, Harness

ITEMS = [
    {"sku": "SKU-0007", "name": "torque wrench", "qty": 4},
    {"sku": "SKU-0031", "name": "hex key set", "qty": 12},
]


class TestPublicRoute(unittest.TestCase):
    def test_health_answers_with_no_caller(self):
        resp = Harness().get("/health")
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.json["status"], "ok")


class TestAuthGate(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def test_anonymous_is_rejected(self):
        resp = self.h.get("/api/items")
        self.assertEqual(resp.status, 401)

    def test_wrong_caller_is_rejected(self):
        resp = self.h.get(
            "/api/items", headers={AUTH_HEADER: "someone-else@example.com"}
        )
        self.assertEqual(resp.status, 401)

    def test_synthetic_caller_passes_the_real_gate(self):
        self.h.seed(r"FROM items", ITEMS)
        resp = self.h.get("/api/items", headers=AUTH_HEADERS)
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.json["requested_by"], TEST_CALLER["email"])


class TestDataRoute(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def test_returns_the_canned_rows(self):
        self.h.seed(r"FROM items", ITEMS)
        resp = self.h.get("/api/items", headers=AUTH_HEADERS)
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.json["items"], ITEMS)
        # The route really queried the (fake) client, and with the shape
        # the handler promises.
        self.assertTrue(self.h.data.ran(r"SELECT sku, name, qty FROM items"))

    def test_unseeded_query_yields_empty_list_not_a_mock(self):
        resp = self.h.get("/api/items", headers=AUTH_HEADERS)
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.json["items"], [])


class TestFlagGate(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def test_flag_off_hides_the_route(self):
        # Nothing seeded the flag, so the store answers OFF: this is the
        # fail-closed default itself under test.
        resp = self.h.get("/api/reorder-report", headers=AUTH_HEADERS)
        self.assertEqual(resp.status, 404)

    def test_flag_on_serves_the_route(self):
        self.h.set_flag("reorder_report", True)
        self.h.seed(
            r"qty < reorder_at", [{"sku": "SKU-0031", "qty": 2, "reorder_at": 6}]
        )
        resp = self.h.get("/api/reorder-report", headers=AUTH_HEADERS)
        self.assertEqual(resp.status, 200)
        self.assertEqual(len(resp.json["reorder"]), 1)

    def test_flag_gate_still_requires_a_caller(self):
        self.h.set_flag("reorder_report", True)
        resp = self.h.get("/api/reorder-report")
        self.assertEqual(resp.status, 401)


if __name__ == "__main__":
    unittest.main()
