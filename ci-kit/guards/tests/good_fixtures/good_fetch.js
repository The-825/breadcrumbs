// Clean fixture for guard_no_raw_fetch: goes through the approved wrapper.
async function loadThing() {
  return fetchAPI("/api/thing");
}
