"""Generated financial invariants; exercises cases beyond the supplied export."""
import unittest
from hypothesis import given, settings, strategies as st
from src.evidence.pipeline import classify

class Properties(unittest.TestCase):
    @settings(max_examples=100, derandomize=True)
    @given(st.lists(st.tuples(st.integers(-10,100), st.integers(-100,10000), st.sampled_from(['INR','USD','EUR'])),max_size=40))
    def test_partition_and_revenue(self, values):
        rows=[dict(order_id=str(i),order_date='2026-08-01',customer_id='C',product_id='P',quantity=str(q),unit_price=str(p),currency=c,status='completed') for i,(q,p,c) in enumerate(values)]
        result=classify(rows,{'C'},{'P'})
        self.assertEqual(len(result),len(rows))
        self.assertEqual(len({r['source_row_number'] for r in result}),len(rows))
        for r in result:
            if r['bucket']=='clean':
                self.assertEqual(r['revenue_paise'],int(r['quantity'])*int(r['unit_price'])*100*(85 if r['currency']=='USD' else 1))
            else: self.assertNotIn('revenue_paise',r)
    @settings(max_examples=100, derandomize=True)
    @given(st.integers(1,10000),st.integers(1,100))
    def test_identical_copies_never_inflate_revenue(self, price, copies):
        row=dict(order_id='A',order_date='2026-09-01',customer_id='C',product_id='P',quantity='1',unit_price=str(price),currency='INR',status='completed')
        result=classify([row.copy() for _ in range(copies)],{'C'},{'P'})
        self.assertEqual(sum(r.get('revenue_paise',0) for r in result),price*100)
        self.assertEqual(sum(r['bucket']=='exact_duplicate_removed' for r in result),copies-1)
