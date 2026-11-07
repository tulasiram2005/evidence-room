import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from src.evidence.pipeline import ROOT
from src.evidence.providers import draft, ProviderFailure, post

class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); (self.root/'results').mkdir()
        for name in ('kpis','ai_claims','evidence'):
            (self.root/'results'/f'{name}.json').write_bytes((ROOT/'results'/f'{name}.json').read_bytes())
    def test_offline_never_connects(self):
        def fail(*args): self.fail('Unexpected network call')
        self.assertEqual(draft(self.root,transport=fail)['provider'],'deterministic_mock')
    def test_free_confirmation_required(self):
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test','GEMINI_MODEL':'gemini-test-flash','GEMINI_FREE_TIER_CONFIRMED':'no'}):
            self.assertEqual(draft(self.root,allow_gemini=True,transport=lambda *args:self.fail('Network'))['provider'],'deterministic_mock')
    def test_success_and_cache(self):
        response=json.loads((self.root/'results/ai_claims.json').read_text())
        def transport(*args): return {'message':{'content':json.dumps(response)}}
        with patch.dict(os.environ,{'OLLAMA_MODEL':'test'}):
            first=draft(self.root,allow_ollama=True,transport=transport)
            second=draft(self.root,allow_ollama=True,transport=lambda *args:self.fail('Cache missed'))
        self.assertEqual(first,second); self.assertEqual(first['provider'],'ollama')
    def test_bad_claim_falls_back(self):
        with patch.dict(os.environ,{'OLLAMA_MODEL':'test'}):
            result=draft(self.root,allow_ollama=True,transport=lambda *args:{'message':{'content':'{}'}})
        self.assertEqual(result['provider'],'deterministic_mock')
        self.assertEqual(len(result['failures']),1)
    def test_arbitrary_endpoint_rejected(self):
        with self.assertRaises(ProviderFailure): post('https://example.com',{}, {})

    def test_native_gemini_claim_verification(self):
        expected=json.loads((self.root/'results/ai_claims.json').read_text())
        calls=[]
        def transport(url,payload,headers):
            calls.append(payload)
            if len(calls)==1:
                return {'candidates':[{'content':{'role':'model','parts':[{'functionCall':{'name':'get_monthly_revenue','args':{}}}]}}]}
            return {'candidates':[{'content':{'parts':[{'text':json.dumps(expected)}]}}]}
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test','GEMINI_MODEL':'gemini-test-flash','GEMINI_FREE_TIER_CONFIRMED':'yes'}):
            result=draft(self.root,allow_gemini=True,native_tools=True,transport=transport)
        self.assertEqual(result['provider'],'gemini')
        self.assertEqual(len(result['tool_trace']),1)
        self.assertTrue(all(c['verdict']=='verified' for c in result['claim_checks']))

    def test_native_unknown_tool_falls_back(self):
        def transport(*args):
            return {'candidates':[{'content':{'parts':[{'functionCall':{'name':'execute_sql','args':{}}}]}}]}
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test','GEMINI_MODEL':'gemini-test-flash','GEMINI_FREE_TIER_CONFIRMED':'yes'}):
            result=draft(self.root,allow_gemini=True,native_tools=True,transport=transport)
        self.assertEqual(result['provider'],'deterministic_mock')
