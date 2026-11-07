import copy
import hashlib
import json
import unittest
from pathlib import Path
from src.evidence.pipeline import ROOT, classify, date_value, safe_cell, run

class Rules(unittest.TestCase):
    def row(self, **changes):
        return dict(dict(order_id='A', order_date='2026-08-01', customer_id='C', product_id='P', quantity='2', unit_price='10', currency='INR', status='completed'), **changes)
    def check(self, changes, reason):
        self.assertEqual(classify([self.row(**changes)], {'C'}, {'P'})[0]['reason_code'], reason)
    def test_exact_duplicate(self):
        records = classify([self.row(), self.row()], {'C'}, {'P'})
        self.assertEqual([r['bucket'] for r in records], ['clean', 'exact_duplicate_removed'])
    def test_conflicts_all_quarantined(self):
        records = classify([self.row(), self.row(unit_price='11'), self.row()], {'C'}, {'P'})
        self.assertTrue(all(r['reason_code'] == 'CONFLICTING_DUPLICATE' for r in records))
    def test_invalid_keys(self):
        self.check({'customer_id': ''}, 'INVALID_CUSTOMER_KEY')
        self.check({'product_id': 'unknown'}, 'INVALID_PRODUCT_KEY')
    def test_non_positive(self):
        for value in ('0', '-1'):
            self.check({'quantity': value}, 'NON_POSITIVE_QUANTITY')
            self.check({'unit_price': value}, 'NON_POSITIVE_PRICE')
    def test_slash_date(self):
        result = classify([self.row(order_date='2026/08/13')], {'C'}, {'P'})[0]
        self.assertEqual(result['flags'], 'DATE_NORMALISED')
        self.assertEqual(result['normalized_date'], '2026-08-13')
    def test_invalid_date(self):
        for value in ('2026-09-31', 'not-a-date', '2026-08/01'):
            self.check({'order_date': value}, 'INVALID_DATE')
    def test_status(self):
        self.check({'status': ' Completed '}, 'TRUSTED')
        self.check({'status': 'COMPLETE'}, 'UNMAPPED_STATUS')
    def test_currency(self):
        self.check({'currency': 'EUR'}, 'UNSUPPORTED_CURRENCY')
        self.assertEqual(classify([self.row(currency='USD')], {'C'}, {'P'})[0]['revenue_paise'], 170000)
    def test_cancelled_refunded(self):
        for value in ('cancelled', 'refunded'):
            self.check({'status': value}, 'NOT_COMPLETED')
    def test_nonfinite_numbers(self):
        self.check({'quantity': 'NaN'}, 'INVALID_QUANTITY')
        self.check({'unit_price': 'Infinity'}, 'INVALID_PRICE')
    def test_csv_safety(self):
        for value in ('=SUM(A1)', '+cmd', '-cmd', '@cmd', '  =cmd'):
            self.assertTrue(safe_cell(value).startswith("'"))
        self.assertEqual(safe_cell('-1'), '-1')
    def test_bucket_partition_many_fixtures(self):
        records = [self.row(order_id=str(i), quantity=str(i-20)) for i in range(100)]
        result = classify(records, {'C'}, {'P'})
        self.assertEqual(len(result), len(records))
        self.assertEqual(len({r['source_row_number'] for r in result}), len(records))
        self.assertEqual(sum(r['bucket'] == 'clean' for r in result), 79)

class Integration(unittest.TestCase):
    def test_reproducible_and_immutable(self):
        inputs = {p: p.read_bytes() for p in (ROOT/'data/raw').glob('*.csv')}
        run()
        paths = list((ROOT/'results').glob('*.json')) + [ROOT/'clean_orders.csv', ROOT/'rejected_orders.csv', ROOT/'executive_summary.md']
        before = {p: p.read_bytes() for p in paths}
        run()
        self.assertTrue(all(p.read_bytes() == content for p, content in before.items()))
        self.assertTrue(all(p.read_bytes() == content for p, content in inputs.items()))
    def test_summary(self):
        text = (ROOT/'executive_summary.md').read_text()
        self.assertTrue(150 <= len(text.split()) <= 250, len(text.split()))
        for label in ('Finding 1', 'Finding 2', 'Uncertainty', 'Next action'):
            self.assertEqual(text.count(label), 1)
    def test_partition(self):
        data = json.loads((ROOT/'results/decisions.json').read_text())
        self.assertEqual(sum(data['buckets'].values()), data['raw_rows'])
