-- Deliberately-bad fixture for guard_no_raw_create_view. Never executed.
-- A raw CREATE OR REPLACE VIEW must fail the guard (views ship through the
-- version-controlled view layer as .sqlx).
CREATE OR REPLACE VIEW `example-project.reporting.example_view` AS
SELECT id, name
FROM `example-project.warehouse.example_table`;
