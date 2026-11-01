# Restore the pre-repair version

- Repository: https://github.com/panli0/2809-reader
- Original `main` commit: `5b668d576c457210ea484e33529e945b5d188dc0`
- Backup branch: `backup/pre-repair-2026-11-01`
- Repair branch: `repair/reader-quality-2026-11-01`

## Restore steps

1. Open the repository's **Branches** page.
2. Select `backup/pre-repair-2026-11-01` to view the preserved version.
3. If the deployment must be rolled back, set its source branch back to the backup branch, or reset `main` to the original commit after reviewing the change.

The backup branch points to the exact pre-repair commit plus this restore note. The repair branch is separate; it has not been merged or deployed.
