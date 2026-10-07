# Automate one handoff

**Status:** public, pattern-only exercise. No transfer automation or staging table ships here.

**Assumes:** a fictional workshop team exports an approved supply list as CSV and copies it to a review folder. You can sketch the transfer without connecting to a real system. Use synthetic rows only.

A copied file can look successful while the receiving folder has an old version or missing rows. Map one transfer and its receipt before automating it.

## Fictional handoff

`approved_supply_list.csv` contains a header and these rows:

```csv
item,quantity
markers,4
paper,8
name_tags,12
```

The current process is: owner approves the list, exporter creates the CSV, operator copies it into a review folder, reviewer checks the received file. A possible automation replaces only the copy step. Approval and review stay with people.

## Your action

Draw one before-and-after handoff map. For each step, name its input, owner, output, and failure signal. Add a receipt that records source filename, source revision or digest, destination filename, expected data-row count, received data-row count, and exception. For this fixture, the expected data-row count is three, based on the CSV shown above. A matching count is a useful check, not proof that every value survived.

## Human check

Open the received synthetic CSV and compare its rows with the approved source. If the file is missing, stale, duplicated, or different, stop the transfer and record the exception. Do not let a successful copy message substitute for the received-file check. Save the map and receipt.

For a fuller change worksheet, see the kit's [small-change worksheet](../../templates/workflow-worksheets/README.md).

**Next:** use the received list for [Make a number explainable](04-make-a-number-explainable.md).
