"""Conservative checks: evidence values, prose numbers, causality and scope."""
import re
from decimal import Decimal

ROOT_KEYS = {'insight_title', 'claims'}
CLAIM_KEYS = {'id', 'text', 'type', 'numbers'}
NUMBER_KEYS = {'label', 'value', 'unit', 'evidence_id'}

def verify(draft, evidence):
    if not isinstance(draft, dict) or set(draft) != ROOT_KEYS or not isinstance(draft['claims'], list) or not isinstance(draft['insight_title'], str):
        raise ValueError('Invalid draft schema')
    checked = []
    seen = set()
    for claim in draft['claims']:
        if not isinstance(claim, dict) or set(claim) != CLAIM_KEYS or claim['type'] not in ('number', 'comparison', 'limitation'):
            raise ValueError('Invalid claim schema')
        if not isinstance(claim['numbers'], list) or not isinstance(claim['text'], str) or not isinstance(claim['id'], str) or claim['id'] in seen:
            raise ValueError('Invalid or duplicate claim')
        seen.add(claim['id'])
        issues, values, checks = [], [], []
        for item in claim['numbers']:
            if set(item) != NUMBER_KEYS or type(item['value']) not in (int, float):
                raise ValueError('Invalid numeric evidence schema')
            value = Decimal(str(item['value']))
            if not value.is_finite(): raise ValueError('Nonfinite claim')
            values.append(value)
            reference = evidence.get(item['evidence_id'])
            verdict = 'unsupported' if reference is None else ('verified' if value == Decimal(str(reference['value'])) and item['unit'] == reference['unit'] else 'mismatch')
            checks.append({'evidence_id': item['evidence_id'], 'verdict': verdict, 'expected': reference})
            if verdict != 'verified': issues.append(verdict)
        for match in re.findall(r'(?<!\w)-?\d+(?:,\d{3})*(?:\.\d+)?', claim['text']):
            if Decimal(match.replace(',', '')) not in values: issues.append('unlinked_number')
        if re.search(r'\b(because|due to|caused by|promotion|campaign|seasonality|outage|pricing change)\b', claim['text'], re.I): issues.append('unsupported_cause')
        if re.search(r'\blifetime\b', claim['text'], re.I) and not re.search(r'not (?:their |true )?lifetime', claim['text'], re.I): issues.append('unsupported_lifetime_scope')
        # A correct number does not establish arbitrary prose as fact.
        allowed = {record['allowed_text'] for record in evidence.values() if 'allowed_text' in record}
        if claim['text'] not in allowed: issues.append('factual_prose_needs_review')
        checked.append({'id': claim['id'], 'text': claim['text'], 'verdict': 'verified' if not issues else ('mismatch' if 'mismatch' in issues else 'unsupported'), 'issues': sorted(set(issues)), 'checks': checks})
    return checked
