import unittest
from src.evidence.verify import verify
class ClaimChecks(unittest.TestCase):
    def draft(self, text='Revenue is 100.', value=100):
        return {'insight_title':'Test', 'claims':[{'id':'C1','type':'number','text':text,'numbers':[{'label':'Revenue','value':value,'unit':'INR','evidence_id':'E1'}]}]}
    def check(self, draft):
        return verify(draft, {'E1':{'value':100,'unit':'INR','allowed_text':'Revenue is 100.'}})[0]
    def test_valid(self): self.assertEqual(self.check(self.draft())['verdict'], 'verified')
    def test_wrong_number(self): self.assertEqual(self.check(self.draft(value=101))['verdict'], 'mismatch')
    def test_cause(self): self.assertIn('unsupported_cause', self.check(self.draft(text='Revenue is 100 because of a campaign.'))['issues'])
    def test_unlinked(self): self.assertIn('unlinked_number', self.check(self.draft(text='Revenue is 100 and growth is 40.'))['issues'])
    def test_scope(self): self.assertIn('unsupported_lifetime_scope', self.check(self.draft(text='These are lifetime customers.'))['issues'])
    def test_unknown_fields(self):
        draft=self.draft(); draft['extra']='bad'
        with self.assertRaises(ValueError): verify(draft, {})
    def test_unverified_prose(self): self.assertIn('factual_prose_needs_review', self.check(self.draft(text='September outperformed August.'))['issues'])
