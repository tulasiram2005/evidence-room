# Optional drafting providers
Core `analysis.py` remains offline and deterministic. It always writes the mock
claims and honest mock verification report. A separate opt-in command validates
providers without silently replacing the graded outputs.

`python tools/draft_ai.py --gemini --ollama`

Gemini requires environment variables GEMINI_API_KEY, GEMINI_MODEL (Flash-class),
and GEMINI_FREE_TIER_CONFIRMED=yes. Confirm the model's current free quota and
billing-disabled project first. Never paste a key into the repository or chat.
Ollama requires OLLAMA_MODEL and an already-running local model at 127.0.0.1:11434.
No model is downloaded automatically.

The chain is Gemini → Ollama → deterministic mock, limited to configured providers.
Each request has a timeout and a bounded response; transient Gemini HTTP failures
retry at most three times with backoff. Redirects and proxy forwarding are refused.
Only computed aggregate evidence is sent. Invalid JSON or unverified claims cause
fallback. No error body or credential is logged.

The ignored results/provider_run.json records the actual prompt, provider/model,
UTC timestamp, evidence-dependent prompt hash, response and verification results.
Successful cached results require the same configuration and evidence hash.
Mock fallback is not cached as a successful remote call.

The eight tools in ai_tools.py are independently callable with schemas. Current
transports use aggregate-grounded structured JSON, not native model-directed tool
calling. That distinction and live validation remain open requirements.
