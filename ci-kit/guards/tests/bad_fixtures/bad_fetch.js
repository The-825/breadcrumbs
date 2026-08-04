// Deliberately-bad fixture for guard_no_raw_fetch. Not loaded by any app.
// A bare fetch() that bypasses the approved wrapper must fail the guard.
async function loadThing() {
  const resp = await fetch("/api/thing");
  return resp.json();
}
