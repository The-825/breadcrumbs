"""A tiny synthetic inventory service, written so the harness seams show.

This is scaffolding, not a framework. Routes live in a plain callable table
so the tests run on stdlib alone; swap in your real app factory and the
harness pattern stays identical. All data here is invented workshop
inventory; none of it is real.

The three seams, visible in create_app():
  * data_client   -> anything with .query(sql, params) returning rows
  * auth_resolver -> callable(request) -> caller dict, or None
  * flag_store    -> anything with .enabled(name) -> bool
"""


class Request:
    def __init__(self, method, path, headers=None, body=None):
        self.method = method.upper()
        self.path = path
        self.headers = dict(headers or {})
        self.body = dict(body or {})


class Response:
    def __init__(self, status, body):
        self.status = status
        self.json = body


class App:
    """Plain-callable route table: (method, path) -> handler(request)."""

    def __init__(self):
        self._routes = {}

    def add_route(self, method, path, handler):
        self._routes[(method.upper(), path)] = handler

    def handle(self, request):
        handler = self._routes.get((request.method, request.path))
        if handler is None:
            return Response(404, {"error": "not found"})
        return handler(request)


def create_app(data_client, auth_resolver, flag_store):
    """Build the app with its three external collaborators injected.

    In a framework app the seams are usually module attributes patched in
    place; injection at the factory keeps this example dependency-free. The
    behavior under test is the same either way.
    """
    app = App()

    def health(request):
        # Public on purpose: the one route that answers with no caller.
        return Response(200, {"status": "ok", "service": "inventory-example"})

    def list_items(request):
        # Gate at the boundary: resolve the caller before touching data.
        # The harness stubs the resolver, never this branch, so a request
        # with no header lands here and gets the real 401.
        caller = auth_resolver(request)
        if caller is None:
            return Response(401, {"error": "authentication required"})
        rows = data_client.query(
            "SELECT sku, name, qty FROM items WHERE floor = ? ORDER BY sku",
            params=("main",),
        )
        return Response(200, {"items": rows, "requested_by": caller["email"]})

    def reorder_report(request):
        caller = auth_resolver(request)
        if caller is None:
            return Response(401, {"error": "authentication required"})
        if not flag_store.enabled("reorder_report"):
            # Flag OFF, or unknown to the store: the route hides entirely.
            return Response(404, {"error": "not found"})
        rows = data_client.query(
            "SELECT sku, qty, reorder_at FROM items WHERE qty < reorder_at",
        )
        return Response(200, {"reorder": rows})

    app.add_route("GET", "/health", health)
    app.add_route("GET", "/api/items", list_items)
    app.add_route("GET", "/api/reorder-report", reorder_report)
    return app
