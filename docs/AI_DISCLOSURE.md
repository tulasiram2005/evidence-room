# Actual AI assistance
Codex read the two supplied planning documents and the original candidate README,
implemented the pipeline, tests, SQL, generated-summary template and documentation.
The plan's supplied totals were compared only after computation from the original CSVs.
Codex detected and fixed an initial repository-root path error during execution.
Planted claim tests actually run: wrong numeric value, unsupported cause,
unlinked prose number, lifetime scope and unsupported factual prose.
The pipeline's drafter is deterministic mock code; no external model was called.
The candidate must independently review the decisions and figures and add only
review actions they actually performed. Time spent has not been invented.

## Subsequent implementation and checks
Codex added eight strictly validated read-only aggregate tools, generated Hypothesis
invariant tests, and optional Gemini/Ollama transports. Provider tests used fake
responses; no live model use is claimed. A security scanner identified Python
assertions that could disappear under optimized execution; explicit ValueError
checks replaced them. Dependency auditing identified old pip/setuptools in the
isolated environment; those tools were upgraded locally, not system-wide.

## Native transport implementation (2026-11-07)
Gemini function calling was implemented against the official API guide (https://ai.google.dev/gemini-api/docs/function-calling). Seven additional offline tests exercise the native loop, argument rejection, call/round limits, signature and ID preservation, claim checking and fallback. These tests use simulated transports, not a live model. The submitted analysis still uses the deterministic mock. Opt-in command: `python tools/draft_ai.py --gemini --native-tools`; credentials remain environment-only and free-tier confirmation is required.
