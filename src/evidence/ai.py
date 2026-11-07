"""Offline structured mock; never described as a live model call."""
import hashlib
from .pipeline import write_json
from .verify import verify

def generate(root, kpis):
    evidence, claims = {}, []
    for index, row in enumerate(kpis['monthly']):
        tag = f'E-{index+1:03}'
        text = f"Trusted completed revenue for {row['order_month']} is {row['revenue_paise']} INR paise."
        # Avoid calendar numerals in model prose; month supplied as a word.
        month = 'August' if index == 0 else 'September'
        text = f"Trusted completed revenue for {month} is {row['revenue_paise']} INR paise."
        evidence[tag] = {'value': row['revenue_paise'], 'unit': 'INR paise', 'source_file': 'results/kpis.json', 'pointer': f'/monthly/{index}/revenue_paise', 'allowed_text': text}
        claims.append({'id': f'C{index+1}', 'text': text, 'type': 'number', 'numbers': [{'label': month, 'value': row['revenue_paise'], 'unit': 'INR paise', 'evidence_id': tag}]})
    prompt = 'Draft trusted monthly revenue claims using only the supplied evidence records. Do not infer causes.'
    draft = {'insight_title': 'Trusted monthly revenue', 'claims': claims}
    checks = verify(draft, evidence)
    write_json(root/'results/evidence.json', evidence)
    write_json(root/'results/ai_claims.json', draft)
    write_json(root/'results/claim_checks.json', checks)
    write_json(root/'results/ai_cache.json', {'provider': 'deterministic_mock', 'model': None, 'prompt': prompt, 'prompt_hash': hashlib.sha256(prompt.encode()).hexdigest(), 'response': draft})
    lines = ['# AI with verification', '', 'Codex assisted implementation and review. This pipeline run uses a deterministic mock, not a live language model. No Gemini or Ollama request was made. This mock does not demonstrate live function calling.', '', '## Actual mock prompt', '', prompt, '', '## Checks', '', '| Claim | Evidence | Value (INR paise) | Verdict |', '|---|---|---:|---|']
    lines += [f"| {c['id']} | {c['numbers'][0]['evidence_id']} | {c['numbers'][0]['value']} | {checks[i]['verdict']} |" for i,c in enumerate(claims)]
    lines += ['', 'Exact structured response: `results/ai_claims.json`. Evidence pointers: `results/evidence.json`.', '', '## Candidate review (pending)', 'Read the SQL and rejection decisions, independently check the figures, and record your own review here. No candidate review has been invented.', '']
    (root/'ai_verification.md').write_text('\n'.join(lines))
