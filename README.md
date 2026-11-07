# Evidence Room

> Revenue dropped in September 2026 versus August 2026. Is it a real business change or a data problem?

An offline, reproducible investigation of supplied synthetic orders. The original
candidate instructions are in `docs/challenge_readme.md`. Core deliverables come
before the optional website. See `executive_summary.md` for the computed findings.

## Run
Requires Python 3.11 or newer.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install pandas==2.3.3
python analysis.py
python -m unittest discover -s tests -v
```
On Windows, activate with `.venv\Scripts\Activate.ps1`.
After dependency installation, analysis and tests run offline. No account, database
server, API key or paid service is required.

## Outputs
- `clean_orders.csv`: trusted completed rows, integer INR paise, lineage and flags.
- `rejected_orders.csv`: all other buckets, raw fields and every applicable reason.
- `queries.sql`: SQLite SQL actually executed by the pipeline.
- `results/data_health.json`, `decisions.json`, `kpis.json`: source health and metrics.
- `results/waterfall.json`: exact signed reconciliation, with mixed-currency warning.
- `results/sensitivity.json`, `flip.json`: conditional scenarios and limitations.
- `executive_summary.md`: generated management summary.
- `ai_verification.md`: actual mock draft and evidence checks, candidate review pending.
- `results/manifest.json`: input/output hashes and dependency versions.

## Verification and decisions
Pandas and SQLite independently compute monthly totals, leading products and cohorts.
Golden tests exercise each financial rule. Repeated execution checks deterministic
outputs and unchanged raw inputs. Claim tests plant deliberately wrong assertions.
See `docs/DECISIONS.md`, `docs/LIMITATIONS.md` and `docs/AI_DISCLOSURE.md`.

Do not treat the naive waterfall base as INR: it mixes currency face values. Row
coverage is a data-quality indicator, not probability that the business answer is true.
The mocked drafter is not a live model. Codex assistance is disclosed honestly.

## Bonus website
```sh
cd web
npm ci
npm run build
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```
Open http://127.0.0.1:4173. The browser reads bundled aggregate evidence only.
The raw and cleaned CSV files are not in the web build.

Run `python3 tools/check.py` at the repository root for a saved test report.
Run `python3 tools/package.py` to create the private submission ZIP beside the repo.
See `docs/STATUS.md` for implemented versus unverified master-prompt requirements.
The screenshot audit command is documented in `docs/DESIGN_ITERATIONS.md`.
