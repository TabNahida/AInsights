# Open-source category mapping fix

## Goal

Restore correct open-weight labels and filters after Artificial Analysis changed
`open_source_categorization` from descriptive labels to compact identifiers.

## Root cause

The static-site builder currently treats a category as open only when its text
contains `open`. Artificial Analysis now emits `permissive` and
`commercial-license`, so both known open-weight categories fall through to
`unknown`. Proprietary models continue to work because `proprietary` is already
recognized.

## Design

Keep the upstream CSV values unchanged and normalize them only at the static
site payload boundary. `open_source_type()` will explicitly recognize
`permissive` and `commercial-license` as `open`, while retaining compatibility
with the previous descriptive `Open Weights (...)` values. Existing
`proprietary` and `closed` handling remains unchanged, and genuinely missing or
unrecognized values remain `unknown`.

This keeps raw source data faithful to Artificial Analysis, fixes every page
and filter through the shared generated payload, and avoids guessing that every
future non-proprietary value is open.

## Verification

- Add regression assertions for `permissive` and `commercial-license` before
  changing the implementation, and verify that they initially fail.
- Keep coverage for the old descriptive open-weight value, proprietary values,
  and missing values.
- Rebuild `docs/data/models.json` and `docs/data/models.js`.
- Assert that all 327 currently known open-weight rows are emitted as `open`
  and that no known category is emitted as `unknown`.
- Run the full unit-test suite and `git diff --check` before committing the
  implementation.

## Scope

No scraper transformation, UI markup change, benchmark change, or source-data
rewrite is required. The generated static-site payload changes only because it
is rebuilt with the corrected mapping.
