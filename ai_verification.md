# AI with verification

Codex assisted implementation and review. This pipeline run uses a deterministic mock, not a live language model. No Gemini or Ollama request was made. This mock does not demonstrate live function calling.

## Actual mock prompt

Draft trusted monthly revenue claims using only the supplied evidence records. Do not infer causes.

## Checks

| Claim | Evidence | Value (INR paise) | Verdict |
|---|---|---:|---|
| C1 | E-001 | 180900000 | verified |
| C2 | E-002 | 113740000 | verified |

Exact structured response: `results/ai_claims.json`. Evidence pointers: `results/evidence.json`.

## Candidate review (pending)
Read the SQL and rejection decisions, independently check the figures, and record your own review here. No candidate review has been invented.
