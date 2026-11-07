"""Conditional bounds without inventing exchange rates or counting conflicts twice."""
from collections import defaultdict
from decimal import Decimal
from .pipeline import MONTHS

def analyze(rows, baseline, classify, orders, customers, products):
    allowed = {'conflict': 'high', 'customer': True, 'product': True, 'status': True}
    repaired = classify(orders, customers, products, allowed)
    high = {m: sum(r.get('revenue_paise', 0) for r in repaired if r['bucket'] == 'clean' and r['order_month'] == m) for m in MONTHS}
    strict = classify(orders, customers, products, {'reject_slash': True})
    low = {m: sum(r.get('revenue_paise', 0) for r in strict if r['bucket'] == 'clean' and r['order_month'] == m) for m in MONTHS}
    unknown_dates = sum(int(Decimal(r['face_value']) * (85 if r['currency'] == 'USD' else 1) * 100) for r in rows if r['reason_code'] == 'INVALID_DATE' and r['currency'] in ('INR', 'USD') and Decimal(r['face_value'] or '0') > 0 and r['status'].strip().lower() == 'completed')
    scenarios = []
    for name, aug, sep in [('combined_favour_august_known_currency', high[MONTHS[0]] + unknown_dates, low[MONTHS[1]]), ('combined_favour_september_known_currency', low[MONTHS[0]], high[MONTHS[1]] + unknown_dates)]:
        scenarios.append({'id': name, 'august_paise': aug, 'september_paise': sep, 'change_paise': sep-aug, 'change_percent': float(Decimal(sep-aug)*100/aug), 'conditional': True})
    foreign = defaultdict(Decimal)
    for r in rows:
        if r['reason_code'] == 'UNSUPPORTED_CURRENCY':
            foreign[(r['order_month'], r['currency'])] += Decimal(r['face_value'] or '0')
    gap = Decimal(baseline[MONTHS[0]]-baseline[MONTHS[1]])/100
    fx = []
    for (month, currency), face in sorted(foreign.items()):
        effect = 1 if month == MONTHS[1] else -1
        threshold = gap / (effect * face) if face else None
        fx.append({'month': month, 'currency': currency, 'face_value': str(face), 'break_even_inr_per_unit': str(threshold) if threshold is not None and threshold >= 0 else None, 'interpretation': 'No nonnegative rate reverses the baseline decline; this adds August revenue.' if threshold is not None and threshold < 0 else 'Conditional rate needed to erase the baseline gap.'})
    stakes = defaultdict(Decimal)
    for r in rows:
        if r['bucket'] == 'rejected' and r['status'].strip().lower() not in ('cancelled', 'refunded'):
            stakes[(r['order_month'], r['currency'])] += max(Decimal(r['face_value'] or '0'), Decimal(0))
    maximum = scenarios[1]['change_paise']
    return scenarios, {'trusted_gap_inr': str(gap), 'materiality_percent': 10,
        'known_currency_conditional_min_change_paise': scenarios[0]['change_paise'],
        'known_currency_conditional_max_change_paise': maximum,
        'conditional_robustness': 'drop_in_all_defined_scenarios' if maximum < 0 else 'fragile',
        'unconditional_bounds': None,
        'additional_september_inr_to_erase_conditional_gap': str(Decimal(max(0, -maximum))/100),
        'invalid_date_positive_known_currency_paise': unknown_dates,
        'foreign_currency': fx,
        'excluded_face_values_by_currency': [{'month': m, 'currency': c, 'face_value': str(v)} for (m,c),v in sorted(stakes.items())],
        'scope': 'Conditional on supplied positive amounts and possible key/status/date repairs. Exact duplicates never reinstated; conflict chooses at most one version. Non-positive amounts cannot be repaired. Unknown-currency amounts are separate, not INR. Arbitrary corrected prices or new transactions are outside these bounds.'}
