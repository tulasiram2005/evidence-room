"""Deterministic analysis of untrusted synthetic exports. No network access."""
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MONTHS = ('2026-08', '2026-09')

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')

def read_csv(path):
    with path.open(newline='', encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))

def date_value(value):
    if not re.fullmatch(r'\d{4}[-/]\d{2}[-/]\d{2}', value):
        return None
    if '-' in value and '/' in value:
        return None
    try:
        return datetime.strptime(value.replace('/', '-'), '%Y-%m-%d').date().isoformat()
    except ValueError:
        return None

def number(value):
    try:
        result = Decimal(value)
        return result if result.is_finite() else None
    except InvalidOperation:
        return None

def safe_cell(value):
    text = str(value)
    stripped = text.lstrip()
    if stripped.startswith(('=', '+', '-', '@')) and number(stripped) is None:
        return "'" + text
    return text

def export_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows({key: safe_cell(row.get(key, '')) for key in fields} for row in rows)

def profile(tables):
    result = {}
    for name, rows in tables.items():
        keys = list(rows[0]) if rows else []
        key = name[:-1] + '_id'
        counts = Counter(row.get(key) for row in rows)
        result[name] = {'rows': len(rows), 'columns': keys,
            'blank_cells': {k: sum(not r[k].strip() for r in rows) for k in keys},
            'repeated_key_groups': sum(v > 1 for v in counts.values())}
    result['orders']['invalid_dates'] = sum(date_value(r['order_date']) is None for r in tables['orders'])
    for col in ('status', 'currency'):
        result['orders'][col + '_values'] = dict(sorted(Counter(r[col] for r in tables['orders']).items()))
    return result

def classify(orders, customers, products, overrides=None):
    options = overrides or {}
    groups = defaultdict(list)
    for row in orders:
        groups[row['order_id']].append(row)
    conflicts = {key for key, rows in groups.items() if len({tuple(r.items()) for r in rows}) > 1}
    seen, output = set(), []
    for index, raw in enumerate(orders, 2):
        r = dict(raw)
        r['source_row_number'] = index
        day = date_value(raw['order_date'])
        qty, price = number(raw['quantity']), number(raw['unit_price'])
        status = raw['status'].strip().lower()
        currency = raw['currency'].strip().upper()
        r.update(order_month=day[:7] if day else 'unattributed', normalized_date=day or '',
                 bucket='clean', reason_code='TRUSTED', flags='DATE_NORMALISED' if day and '/' in raw['order_date'] else '')
        signature = tuple(raw.items())
        reason = None
        if raw['order_id'] in conflicts:
            reason = 'CONFLICTING_DUPLICATE'
            if options.get('conflict'):
                candidates = groups[raw['order_id']]
                selected = sorted(candidates, key=lambda a: (number(a['quantity']) or Decimal(0)) * (number(a['unit_price']) or Decimal(0)))
                selected = selected[0 if options['conflict'] == 'low' else -1]
                if raw == selected and raw['order_id'] not in seen:
                    reason = None
                    seen.add(raw['order_id'])
        elif signature in seen:
            reason = 'EXACT_DUPLICATE_REMOVED'
        seen.add(signature)
        reasons = []
        if not raw['order_id'].strip(): reasons.append('INVALID_ORDER_KEY')
        if status in ('cancelled', 'refunded'): reasons.append('NOT_COMPLETED')
        if not day: reasons.append('INVALID_DATE')
        elif day[:7] not in MONTHS: reasons.append('OUTSIDE_WINDOW')
        if raw['customer_id'] not in customers and not options.get('customer'): reasons.append('INVALID_CUSTOMER_KEY')
        if raw['product_id'] not in products and not options.get('product'): reasons.append('INVALID_PRODUCT_KEY')
        if qty is None: reasons.append('INVALID_QUANTITY')
        elif qty <= 0: reasons.append('NON_POSITIVE_QUANTITY')
        if price is None: reasons.append('INVALID_PRICE')
        elif price <= 0: reasons.append('NON_POSITIVE_PRICE')
        if day and '/' in raw['order_date'] and options.get('reject_slash'): reasons.append('DATE_FORMAT_REJECTED')
        if status not in ('completed', 'cancelled', 'refunded') and not options.get('status'): reasons.append('UNMAPPED_STATUS')
        if currency not in ('INR', 'USD') and not options.get('currency_face'): reasons.append('UNSUPPORTED_CURRENCY')
        reason = reason or (reasons[0] if reasons else None)
        r['all_reasons'] = '|'.join(dict.fromkeys(([reason] if reason else []) + reasons))
        r['face_value'] = str(qty * price) if qty is not None and price is not None else ''
        if reason:
            r['reason_code'] = reason
            r['bucket'] = {'EXACT_DUPLICATE_REMOVED': 'exact_duplicate_removed', 'NOT_COMPLETED': 'not_completed'}.get(reason, 'rejected')
        else:
            amount = qty * price * (85 if currency == 'USD' else 1)
            scaled = amount * 100
            if scaled != scaled.to_integral_value():
                raise ValueError('Sub-paise precision requires an explicit rounding decision')
            r['revenue_paise'] = int(scaled)
        r['reason_text'] = r['reason_code'].replace('_', ' ').capitalize()
        output.append(r)
    return output

def totals(rows):
    return {m: sum(r['revenue_paise'] for r in rows if r['bucket'] == 'clean' and r['order_month'] == m) for m in MONTHS}

def run():
    results = ROOT / 'results'
    results.mkdir(exist_ok=True)
    hashes_path = ROOT / 'data/raw.sha256'
    actual_inputs = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'data/raw').glob('*.csv'))}
    if hashes_path.exists() and json.loads(hashes_path.read_text()) != actual_inputs:
        raise ValueError('Raw input integrity check failed; review changed source files explicitly.')
    tables = {name: read_csv(ROOT / 'data/raw' / (name + '.csv')) for name in ('orders', 'customers', 'products')}
    for table, key in (('customers', 'customer_id'), ('products', 'product_id')):
        identifiers = [r[key] for r in tables[table]]
        if len(set(identifiers)) != len(identifiers) or any(not x.strip() for x in identifiers):
            raise ValueError('Master keys must be unique and nonblank: ' + table)
    write_json(results / 'data_health.json', profile(tables))
    rows = classify(tables['orders'], {r['customer_id'] for r in tables['customers']}, {r['product_id'] for r in tables['products']})
    clean = [r for r in rows if r['bucket'] == 'clean']
    fields = list(tables['orders'][0]) + ['source_row_number', 'normalized_date', 'order_month', 'bucket', 'reason_code', 'reason_text', 'all_reasons', 'flags', 'face_value', 'revenue_paise']
    export_csv(ROOT / 'clean_orders.csv', clean, fields)
    export_csv(ROOT / 'rejected_orders.csv', [r for r in rows if r['bucket'] != 'clean'], fields)
    write_json(results / 'decisions.json', {'buckets': dict(Counter(r['bucket'] for r in rows)), 'primary_reasons': dict(Counter(r['reason_code'] for r in rows)), 'raw_rows': len(rows)})
    store = sqlite3.connect(':memory:')
    store.execute('CREATE TABLE clean_orders(order_id TEXT, order_date TEXT, customer_id TEXT, product_id TEXT, order_month TEXT, revenue_paise INTEGER)')
    store.executemany('INSERT INTO clean_orders VALUES (?,?,?,?,?,?)', [(r['order_id'], r['normalized_date'], r['customer_id'], r['product_id'], r['order_month'], r['revenue_paise']) for r in clean])
    store.execute('CREATE TABLE products(product_id TEXT, product_name TEXT, category TEXT)')
    store.executemany('INSERT INTO products VALUES (?,?,?)', [(r['product_id'], r['product_name'], r['category']) for r in tables['products']])
    store.execute('CREATE TABLE audit_rows(source_row_number INTEGER, order_month TEXT, bucket TEXT, reason_code TEXT, completed_like INTEGER, face_paise INTEGER, trusted_paise INTEGER)')
    store.executemany('INSERT INTO audit_rows VALUES (?,?,?,?,?,?,?)', [(r['source_row_number'], r['order_month'], r['bucket'], r['reason_code'], int(r['status'].strip().lower() not in ('cancelled','refunded')), int(Decimal(r['face_value'] or '0')*100), r.get('revenue_paise',0)) for r in rows])
    kpis = {}
    query_text = (ROOT / 'sql/queries.sql').read_text()
    for block in query_text.split('-- query: ')[1:]:
        name, query = block.split('\n', 1)
        cursor = store.execute(query.strip())
        kpis[name] = [dict(zip([x[0] for x in cursor.description], record)) for record in cursor.fetchall()]
    (ROOT / 'queries.sql').write_text(query_text)
    df = pd.DataFrame(clean)
    independent = {m: int(df.loc[df.order_month == m, 'revenue_paise'].sum()) for m in MONTHS}
    sql_totals = {r['order_month']: r['revenue_paise'] for r in kpis['monthly']}
    assert independent == sql_totals, 'Pandas/SQL monthly mismatch'
    pandas_top = df.groupby('product_id').revenue_paise.sum().sort_values(ascending=False)
    sql_top = {r['product_id']: r['revenue_paise'] for r in kpis['top_products']}
    assert {k: int(v) for k,v in pandas_top.head(10).items()} == sql_top
    df['first'] = df.groupby('customer_id').normalized_date.transform('min')
    df['cohort'] = df.apply(lambda r: 'new' if r.normalized_date == r['first'] else 'repeat', axis=1)
    for r in kpis['cohorts']:
        subset = df[(df.order_month == r['order_month']) & (df.cohort == r['cohort'])]
        assert (int(subset.revenue_paise.sum()), len(subset), subset.customer_id.nunique()) == (r['revenue_paise'], r['orders'], r['customers'])
    for row in kpis['reconciliation']:
        assert row['naive_mixed_currency_face_paise'] + row['excluded_delta_paise'] + row['conversion_delta_paise'] == row['trusted_revenue_paise']
    write_json(results / 'kpis.json', kpis)
    write_json(results / 'parity.json', {'monthly': True, 'top_products': True, 'cohorts': True})
    waterfall = {}
    for month in MONTHS:
        relevant = [r for r in rows if r['order_month'] == month and r['status'].strip().lower() not in ('cancelled', 'refunded')]
        naive = sum(Decimal(r['face_value'] or '0') for r in relevant)
        deltas = defaultdict(Decimal)
        for r in relevant:
            face = Decimal(r['face_value'] or '0')
            if r['bucket'] != 'clean': deltas[r['reason_code']] -= face
            else: deltas['USD_CONVERSION_EFFECT'] += Decimal(r['revenue_paise']) / 100 - face
        end = naive + sum(deltas.values())
        assert end * 100 == independent[month]
        waterfall[month] = {'naive_mixed_currency_face_value': str(naive), 'deltas': {k: str(v) for k,v in sorted(deltas.items())}, 'trusted_inr': str(end), 'warning': 'Face values mix currencies; ratio is not monetary coverage.', 'trusted_row_share': sum(r['bucket'] == 'clean' for r in relevant) / len(relevant)}
    write_json(results / 'waterfall.json', waterfall)
    scenarios = []
    for name, options in [('baseline', {}), ('conflict_low', {'conflict': 'low'}), ('conflict_high', {'conflict': 'high'}), ('accept_customer', {'customer': True}), ('accept_product', {'product': True}), ('reject_slash', {'reject_slash': True}), ('map_status', {'status': True}), ('unsupported_face_only', {'currency_face': True})]:
        values = totals(classify(tables['orders'], {r['customer_id'] for r in tables['customers']}, {r['product_id'] for r in tables['products']}, options))
        aug, sep = [values[m] for m in MONTHS]
        scenarios.append({'id': name, 'august_paise': aug, 'september_paise': sep, 'change_paise': sep-aug, 'change_percent': float(Decimal(sep-aug) * 100 / aug), 'conditional': name == 'unsupported_face_only'})
    from .sensitivity import analyze
    combined, flip = analyze(rows, independent, classify, tables['orders'], {r['customer_id'] for r in tables['customers']}, {r['product_id'] for r in tables['products']})
    scenarios.extend(combined)
    write_json(results / 'sensitivity.json', scenarios)
    write_json(results / 'flip.json', flip)
    from .summary import generate
    generate(ROOT, kpis, scenarios, rows)
    from .ai import generate as generate_ai
    generate_ai(ROOT, kpis)
    from .export import export
    export(ROOT, rows)
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'data/raw').glob('*.csv'))}
    write_json(ROOT / 'data/raw.sha256', hashes)
    write_json(results / 'manifest.json', {'inputs': hashes, 'pandas_version': pd.__version__, 'rules_code_hash': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'output_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(results.glob('*.json')) if p.name != 'manifest.json'}})
    print(json.dumps({'buckets': dict(Counter(r['bucket'] for r in rows)), 'monthly_paise': independent, 'parity': 'passed'}, indent=2))
