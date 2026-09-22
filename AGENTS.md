# Repository working instructions

- Work directly on `main`. Do not create feature branches or worktrees unless the user explicitly requests one. Preserve local changes and synchronize remote updates without resetting work.
- For model coverage requests, read `docs/guides/model-data-research.md`, research current public sources, and implement supported data updates. A gap report alone does not complete a request to add missing model data.
- For subscription price research, read `docs/guides/token-plan-pricing-research.md` and retain source-backed inputs and reproducible calculations.
- Update maintained sources and parsers, rebuild affected generated artifacts, and validate exact model/configuration matching. Never manufacture scores or change ranking weights to meet expectations about a named model.
- Commit and push when requested by the user. Do not create a pull request or a separate branch as a substitute for an authorized direct update to `main`.
