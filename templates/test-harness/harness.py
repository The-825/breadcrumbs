"""In-process test harness: boot the real app, fake only the edges.

A parse check proves a file compiles. This harness proves the next layer up:
real route behavior (auth gate, query construction, response shape) with no
network, no credentials, and no deployed environment. Stdlib only, so the
tests run anywhere Python runs and CI needs no install step.

Exactly three seams are faked, nothing else:
  * data client   -> FakeDataClient: seeded (pattern -> rows), records queries
  * auth resolver -> stub_auth_resolver: one fixed synthetic caller
  * flag store    -> FakeFlagStore: every flag OFF unless a test sets it

Usage:
    from harness import AUTH_HEADERS, Harness

    class TestMyRoute(unittest.TestCase):
        def setUp(self):
            self.h = Harness()
            self.h.seed(r"FROM items", [{"sku": "SKU-0007", "qty": 4}])

        def test_route(self):
            resp = self.h.get("/api/items", headers=AUTH_HEADERS)
            self.assertEqual(resp.status, 200)

Fixtures are synthetic by construction: placeholder emails on example.com,
identifiers shaped nothing like production ones, no rows copied from a real
store.
"""
import re

import app_example

# The one synthetic caller every authenticated test speaks as.
TEST_CALLER = {"email": "test-operator@example.com", "role": "admin"}
AUTH_HEADER = "X-Authenticated-User"
AUTH_HEADERS = {AUTH_HEADER: TEST_CALLER["email"]}


class FakeDataClient:
    """Pattern-to-rows query router standing in for the real data client.

    Records every query for assertions. Unmatched queries return an empty
    list, never a loose mock, so code that mishandles an empty result fails
    loudly instead of passing by accident.
    """

    def __init__(self):
        self._fixtures = []   # list[(compiled_regex, rows)]
        self.queries = []     # list[(sql, params)]

    def seed(self, pattern, rows):
        # Later seeds win: inserted at the front, checked first.
        self._fixtures.insert(0, (re.compile(pattern, re.I | re.S), list(rows)))

    def query(self, sql, params=()):
        self.queries.append((sql, tuple(params)))
        for rx, rows in self._fixtures:
            if rx.search(sql):
                return [dict(row) for row in rows]
        return []

    def ran(self, pattern):
        """True if any recorded query matches `pattern`."""
        rx = re.compile(pattern, re.I | re.S)
        return any(rx.search(sql) for sql, _params in self.queries)


def stub_auth_resolver(request):
    """Resolve the fixed synthetic caller, or nobody.

    Correct header -> the test caller. Absent or wrong header -> None, which
    sends the app down its REAL rejection branch; the gate itself is never
    bypassed.
    """
    if request.headers.get(AUTH_HEADER) == TEST_CALLER["email"]:
        return dict(TEST_CALLER)
    return None


class FakeFlagStore:
    """Flag store forced to a known state: OFF unless a test turns it on.

    The OFF default doubles as the fail-closed proof: a route behind a flag
    nobody seeded must behave as if the flag system said no.
    """

    def __init__(self, flags=None):
        self._flags = dict(flags or {})

    def enabled(self, name):
        return bool(self._flags.get(name, False))

    def set_flag(self, name, value):
        self._flags[name] = bool(value)


class Harness:
    """Boot the real app with the three fakes wired in; drive it in-process.

    One Harness per test: fresh fakes each time, no cross-test bleed. Point
    `app_factory` at your own app's factory to reuse the harness beyond the
    example app; the factory must accept the three seams as keyword args.
    """

    def __init__(self, app_factory=app_example.create_app):
        self.data = FakeDataClient()
        self.flags = FakeFlagStore()
        self.app = app_factory(
            data_client=self.data,
            auth_resolver=stub_auth_resolver,
            flag_store=self.flags,
        )

    # -- fixture surface ----------------------------------------------------
    def seed(self, pattern, rows):
        self.data.seed(pattern, rows)

    def set_flag(self, name, value):
        self.flags.set_flag(name, value)

    # -- test client --------------------------------------------------------
    def get(self, path, headers=None):
        return self.app.handle(app_example.Request("GET", path, headers=headers))

    def post(self, path, body=None, headers=None):
        return self.app.handle(
            app_example.Request("POST", path, headers=headers, body=body)
        )
