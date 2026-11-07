import json
import re
import sqlite3
import unittest
from decimal import Decimal
from src.evidence.pipeline import ROOT, classify
class EvidenceChecks(unittest.TestCase):
    def test_waterfall(self):
        data=json.loads((ROOT/'results/waterfall.json').read_text())
        for row in data.values():
            self.assertEqual(Decimal(row['naive_mixed_currency_face_value'])+sum(Decimal(v) for v in row['deltas'].values()),Decimal(row['trusted_inr']))
    def test_conflict_sensitivity_keeps_one(self):
        base={'order_id':'A','order_date':'2026-08-01','customer_id':'C','product_id':'P','quantity':'1','unit_price':'10','currency':'INR','status':'completed'}
        other=dict(base,unit_price='20')
        for mode, expected in [('low',1000),('high',2000)]:
            rows=classify([base,other,base],{'C'},{'P'},{'conflict':mode})
            clean=[r for r in rows if r['bucket']=='clean']
            self.assertEqual(len(clean),1)
            self.assertEqual(clean[0]['revenue_paise'],expected)
    def test_summary_numbers(self):
        kpis=json.loads((ROOT/'results/kpis.json').read_text())
        scenarios=json.loads((ROOT/'results/sensitivity.json').read_text())
        expected={Decimal(1),Decimal(2)}
        for row in kpis['monthly']:
            expected.update([Decimal(row['revenue_paise'])/100,Decimal(row['orders'])])
        expected.add(Decimal(str(scenarios[0]['change_percent'])).quantize(Decimal('.01')))
        text=(ROOT/'executive_summary.md').read_text()
        for value in re.findall(r'-?\d+(?:,\d{3})*(?:\.\d+)?',text):
            self.assertIn(Decimal(value.replace(',','')),expected)
    def test_same_day_window(self):
        db=sqlite3.connect(':memory:')
        db.execute('CREATE TABLE clean_orders(order_date TEXT,customer_id TEXT,order_month TEXT,revenue_paise INTEGER)')
        db.executemany('INSERT INTO clean_orders VALUES (?,?,?,?)',[('2026-08-01','C','2026-08',100),('2026-08-01','C','2026-08',200),('2026-08-02','C','2026-08',300),('2026-09-01','D','2026-09',400)])
        sql=(ROOT/'sql/queries.sql').read_text().split('-- query: cohorts\n')[1].split('-- query: health')[0]
        rows=db.execute(sql).fetchall()
        self.assertEqual(rows,[('2026-08','new',300,2,1),('2026-08','repeat',300,1,1),('2026-09','new',400,1,1)])
    def test_site_payload_no_customer_or_full_orders(self):
        text=(ROOT/'web/src/evidence.json').read_text()
        for forbidden in ('Customer 001','"C001"','clean_orders','/Users/','@srmist'):
            self.assertNotIn(forbidden,text)
    def test_csp(self):
        headers=(ROOT/'web/public/_headers').read_text()
        for required in ("default-src 'self'","connect-src 'none'","frame-ancestors 'none'","object-src 'none'"):
            self.assertIn(required,headers)
