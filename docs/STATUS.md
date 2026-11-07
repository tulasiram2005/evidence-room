# Measured implementation status — 2026-11-07

## Implemented and exercised
- Original candidate README and all three CSVs read; source copies preserved.
- String ingestion, missingness/schema/status/currency profile and input hashes.
- Finance trust rules, reason-coded exports, all-row partition and safe CSV text.
- Executed SQLite monthly revenue, overall/monthly products, windowed cohorts,
  health, exclusions and reconciliation queries.
- Independent pandas monthly/overall-top-products/cohort parity.
- Exact signed reconciliation, eight individual scenarios and two conditional
  combined scenarios; currency-aware break-even explanation.
- Executive summary within 150–250 words and numerical traceability test.
- Structured mock draft, evidence references and planted-error claim checks.
- React/TypeScript static site, both themes, charts, receipts and scenario controls.
- Actual main in-app-browser checks: theme switch, scenario values, receipt filter.
- Local tests and build; recorded results in results/test_report.json and npm_audit.json.
- Public GitHub repository backed up; static hosting uses Vercel Hobby, with no paid service enabled.

- Hypothesis suite: two properties with 100 generated cases each.
- 46 tests passed; local security scans passed after isolated toolchain upgrades.

- Baseline plus three design revisions passed: 320 screenshots; eight theme/viewport combinations per run; no reported axe violations, console errors or external requests.
- Local Lighthouse: performance 100, accessibility 100, best practices 100, SEO 82. Meta description and robots.txt fixes build successfully; their effect has not been remeasured.
- Vercel dashboard identifies the selected workspace as Hobby (checked 2026-11-07). Static deployment is READY; HTTP/asset/header checks passed. Hosted interactions remain unverified.

## Remaining optional features and verification
- Hosted CI execution and remaining SQL lint/type gates. Python transitive lock, local Ruff/Bandit/pip-audit and TypeScript build checks are implemented.
- Eight aggregate tools and optional Gemini/Ollama JSON transports implemented and unit-tested. Bounded Gemini native function calling is implemented with preserved call IDs/signatures, strict tool validation, three rounds/eight calls maximum, and fallback tests. Live provider validation remains unmeasured.
- The complete custom design specification (fonts, every-number evidence drawers,
  animated waterfall/bounds visuals, copy controls and shortcut sheet).
- Complete hosted interaction regression (browser control became unavailable).
- Candidate's independent review, personalized explanation and actual submission.

## Important analytical adjustments
No ratio mixing foreign-currency face values with INR is presented as monetary
confidence. Trusted row coverage is used instead and explicitly defined.
Unknown rates are not invented. Bounds are conditional on documented repairs;
there is no finite unconditional bound over arbitrary missing/corrected transactions.

No tests, scores, candidate actions or hosted runs are claimed without evidence.
