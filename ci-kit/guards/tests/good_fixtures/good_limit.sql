-- Clean fixture for guard_no_magic_limit: row cap is a bound parameter, no literal.
SELECT id, name
FROM `example-project.warehouse.example_table`
LIMIT @row_limit;
