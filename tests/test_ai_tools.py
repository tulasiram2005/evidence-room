import unittest
from src.evidence.ai_tools import EvidenceTools, schemas
from src.evidence.pipeline import ROOT

class ToolTests(unittest.TestCase):
    def setUp(self): self.tools = EvidenceTools(ROOT)
    def test_all_eight_tools(self):
        for schema in schemas():
            args = {'month': '2026-08'} if schema['name'] == 'get_waterfall' else {'limit': 3} if schema['name'] == 'get_top_products' else {}
            result = self.tools.call(schema['name'], args)
            self.assertTrue(result)
            for row in result:
                self.assertEqual(set(row), {'evidence_id','source_file','pointer','value'})
    def test_bad_arguments(self):
        for name, args in [('get_data_health', {'path':'/etc/passwd'}), ('get_waterfall',{}), ('get_top_products',{'limit':True}), ('get_top_products',{'limit':11}), ('get_monthly_revenue',{'month':'2026-10'}), ('get_exclusions',{'reason_code':'DROP TABLE'}), ('unknown',{})]:
            with self.assertRaises(ValueError): self.tools.call(name,args)
    def test_month_filter(self):
        result = self.tools.call('get_monthly_revenue',{'month':'2026-09'})
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['value']['order_month'],'2026-09')
        self.assertEqual(result[0]['pointer'],'/monthly/1')
    def test_no_raw_cell_text(self):
        result = self.tools.call('get_top_products', {'limit':10})
        self.assertTrue(all('product_name' not in r['value'] and 'category' not in r['value'] for r in result))
        health=self.tools.call('get_data_health',{})[0]['value']
        self.assertNotIn('status_values',health['orders'])
