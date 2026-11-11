-- Proposed local database shape only. The pilot does not create a database.
PRAGMA foreign_keys = ON;
CREATE TABLE workflow_definition (
  id TEXT PRIMARY KEY,
  schema_version INTEGER NOT NULL CHECK(schema_version = 1),
  fields_json TEXT NOT NULL
);
CREATE TABLE intake_record (
  id TEXT PRIMARY KEY CHECK(id LIKE 'SYN-%'),
  workflow_id TEXT NOT NULL REFERENCES workflow_definition(id),
  values_json TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('new','held','follow_up','done')),
  review_json TEXT NOT NULL DEFAULT '{}',
  delivery_json TEXT NOT NULL DEFAULT '{}',
  holds_json TEXT NOT NULL DEFAULT '[]',
  draft TEXT NOT NULL DEFAULT '',
  outcome TEXT NOT NULL DEFAULT '',
  CHECK(state <> 'done' OR length(trim(outcome)) > 0)
);
CREATE TABLE activity (
  sequence INTEGER PRIMARY KEY,
  record_id TEXT NOT NULL REFERENCES intake_record(id),
  event_type TEXT NOT NULL,
  detail TEXT NOT NULL,
  recorded_at TEXT NOT NULL
);
