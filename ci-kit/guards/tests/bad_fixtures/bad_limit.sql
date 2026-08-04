-- Deliberately-bad fixture for guard_no_magic_limit. Never executed.
-- A hardcoded numeric LIMIT must fail the guard.
SELECT id, name
FROM `example-project.warehouse.example_table`
LIMIT 100;
