# Security controls and evidence
- Core pipeline imports no network client and makes no network requests.
- Original inputs copied unchanged; SHA-256 manifest and immutability integration test.
- SQL inserts use bound parameters; no CSV text interpolated into SQL.
- Formula-injection protection in safe_cell; tests include whitespace and negative numbers.
- No credentials required, printed or committed. Environment files ignored.
- Static publication must exclude raw/clean files and customer names/keys.
- Local repository is not public. No deployment has been made.
- Numeric claim schema rejects unknown fields and nonfinite numbers.
- Candidate must inspect submission for personal details before sharing.
- Dependency audits and hosted CI are pending until executed; they are not claimed passed.

## Additional measured checks
The Python 3.11 environment was audited with pip-audit; old pip/setuptools findings
were fixed by upgrading the isolated environment. Current report is in
results/pip_audit.json. Bandit findings about disableable assertions were fixed;
core invariants now raise ValueError even under optimized Python execution.
The repository-history pattern scan is in results/publication_check.json. It is
an aid to review, not a guarantee that arbitrary sensitive content is detectable.
Provider transports reject redirects/unapproved hosts, limit response bytes and
use bounded timeouts/retries. Live provider execution remains unverified.
