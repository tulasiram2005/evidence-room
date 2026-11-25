# Evidence Room architecture

Evidence Room separates offline computation from static presentation. Python
produces the evidence; the browser renders a checked subset, and downloadable BI snapshots preserve the published case. There is no hosted
Python API, database service, authentication service or runtime model connection.

## Data flow and verification

```mermaid
flowchart TB
    subgraph Offline[Offline analysis on the developer or reviewer laptop]
        Raw["orders.csv / customers.csv / products.csv"] --> Integrity["SHA-256 integrity check"]
        Integrity --> Ingest["String ingestion + source row numbers"]
        Ingest --> Profile["Data-health snapshot"]
        Ingest --> Rules["Validation and finance trust decisions"]
        Rules --> Clean["Trusted completed orders"]
        Rules --> Excluded["Rejected, duplicate and not-completed rows"]
        Clean --> SQL["In-memory SQLite + executed queries.sql"]
        Clean --> Pandas["Independent pandas calculations"]
        SQL --> Parity["Exact parity checks"]
        Pandas --> Parity
        Excluded --> Reconcile["Reason-coded reconciliation and repair scenarios"]
        Parity --> Reconcile
        Reconcile --> Results["JSON results, CSV exports, management summary, manifest"]
        Results --> Mock["Deterministic mock draft"]
        Mock --> Verify["Claim checker: number, evidence, cause and scope checks"]
    end
    Results --> Metrics["Monthly revenue, August adjustments and disposition counts"]
    Metrics --> PowerBI["Power BI import model and report"]
    Metrics --> Tableau["Tableau Hyper extracts and dashboard"]
    Results --> Audit["Excel row audit, reconciliation and repair scenarios"]
    Results --> Export["Allowlisted export.py payload"]
    Verify --> Export
    Export --> Bundle["web/src/evidence.json + React / TypeScript / CSS"]
    Bundle --> Build["Vite static build + publication check"]
    Build --> Browser["Local static server or Vercel Hobby CDN"]
```

The rule engine partitions every raw row into exactly one disposition. The sum
must equal the input row count. Money is parsed with Decimal and retained as
integer INR paise. SQL and pandas results must agree before publication. The
pipeline records source/output hashes; repeat runs are tested for determinism.

## Business intelligence and row-level audit

| Deliverable | Source and grain | What a reviewer can verify |
|---|---|---|
| [Power BI project](../dashboard/Power-BI.zip) | Embedded Power Query M tables hold one row per month, August adjustment or disposition. The PBIR report references its sibling import model by relative path. | Three native visuals compare monthly revenue, bridge the August balance and count row dispositions. Refresh reloads the packaged tables. |
| [Tableau workbook](../dashboard/Evidence-Room.twbx) | The TWBX contains two Hyper extracts: order counts and trusted revenue by month and disposition, and the nine signed August adjustments. | The Revenue review dashboard combines the monthly chart, signed reconciliation and data-quality counts. |
| [Excel audit](../dashboard/Revenue-audit.xlsx) | The clean and excluded CSVs supply one classified record per original order row. The workbook retains source dates, keys, quantities, prices, currencies, statuses, row numbers and exception codes. A keyed lookup links each policy assignment to its row amount even after sorting the audit table. | Formula-driven sheets tie the 244 records to monthly totals, test the August closing balance and split the monthly change into order-count and average-value contributions. |

These files are versioned snapshots. When inputs or recognition rules change, rerun the pipeline, update the BI files from the resulting exports, and check them against the new totals before publishing. For the August–September release, the checks are 113 and 84 trusted orders, INR 1,809,000 and INR 1,137,400 in trusted revenue, and zero residual in both Excel reconciliations. The [dashboard index](../dashboard/) and [project report](Evidence-Room-Project-Report.pdf) link the release artifacts.

## Optional provider path

```mermaid
flowchart LR
    User["Explicit provider opt-in"] --> Gate["Free-tier / model / credential checks"]
    Gate --> Gemini["Gemini Flash REST"]
    Gemini --> Tools["Eight allowlisted aggregate tools"]
    Tools --> Gemini
    Gemini --> Check["Strict claim verification"]
    Gemini -. failure .-> Ollama["Local Ollama JSON transport"]
    Ollama --> Check
    Ollama -. failure .-> Mock["Deterministic mock"]
    Check -. invalid claim .-> Mock
    Check --> Log["Private provider_run.json cache and trace"]
    Mock --> Log
```

Provider transport is separate from `analysis.py`. Gemini native calls allow at
most three rounds and eight tool calls. Tool names and arguments are validated;
no model-supplied shell commands, SQL or arbitrary paths are executed. Model
messages preserve function-call IDs and thought signatures. Only aggregate
results and evidence references are returned to the model. Transport uses bounded
responses, timeouts and retries; failed or unverified drafts fall back.

The committed analytical evidence uses the deterministic mock. Live-model
validation remains unmeasured. See [provider details](PROVIDERS.md).

## Implementation map

| Component | File | Responsibility |
|---|---|---|
| Entry point | `analysis.py` | Run the offline pipeline |
| Core pipeline | `src/evidence/pipeline.py` | Ingestion, health, trust rules, exports, SQL and parity |
| Sensitivity | `src/evidence/sensitivity.py` | Explicit repair scenarios and conditional bounds |
| Summary | `src/evidence/summary.py` | Generate traceable management text |
| Default draft | `src/evidence/ai.py` | Deterministic claims and verification report |
| Tool interface | `src/evidence/ai_tools.py` | Strict read-only aggregate schemas and evidence pointers |
| Provider orchestration | `src/evidence/providers.py`, `native_tools.py` | Opt-in transport, native loop, cache and fallback |
| Claim verification | `src/evidence/verify.py` | Schema, factual and numerical checks |
| Website boundary | `src/evidence/export.py` | Export allowed fields into static JSON |
| Presentation | `web/src/main.tsx`, `style.css` | Narrative sections, charts, receipts and interactions |
| Publication gate | `tools/build_gate.py` | Reject forbidden files/content in static output |

## Security and publication boundaries

- The public Git repository contains synthetic source data, reproducible code,
  project documentation and test evidence.
- The website contains aggregates and selected rejection fields. Full raw/clean
  CSVs stay outside the deployed output.
- Keys belong in environment variables; private provider logs and `.env` files
  are excluded from Git and the submission archive.
- Browser policy disallows runtime connections (`connect-src 'none'`); scripts,
  styles and fonts are same-origin. No analytics or third-party CDN assets are used.
- Vercel builds the `web` directory and serves `dist`; it does not rerun the Python
  analysis. Developers regenerate `web/src/evidence.json` locally before pushing
  changes that affect results.
- The manual GitHub Actions workflow performs verification; a hosted successful
  run is not yet part of the measured evidence.

## Evidence and known boundaries

[Tests](../results/test_report.json), [parity](../results/parity.json),
[browser audit](../results/ui.json), [Lighthouse](../results/lighthouse.json) and
[hosted HTTP checks](../results/hosted_smoke.json) provide distinct evidence.
Local UI success does not prove hosted interaction success. See
[implementation status](STATUS.md) for outstanding work.
