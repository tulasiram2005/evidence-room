import copy
import unittest
from src.evidence.native_tools import generate
from src.evidence.ai_tools import EvidenceTools
from src.evidence.pipeline import ROOT


class NativeToolTests(unittest.TestCase):
    def setUp(self):
        self.payload = {'contents': [{'role': 'user', 'parts': [{'text': 'Draft JSON'}]}],
                        'generationConfig': {'responseMimeType': 'application/json'}}
        self.tools = EvidenceTools(ROOT)

    def test_round_trip_preserves_signature_and_id(self):
        original = copy.deepcopy(self.payload)
        message = {'role': 'model', 'parts': [{'thoughtSignature': 'opaque', 'functionCall':
                    {'id': 'call-1', 'name': 'get_monthly_revenue', 'args': {'month': '2026-08'}}}]}
        seen = []
        def transport(url, payload, headers):
            seen.append(copy.deepcopy(payload))
            if len(seen) == 1:
                return {'candidates': [{'content': message}]}
            return {'candidates': [{'content': {'parts': [{'text': '{"ok":true}'}]}}]}
        result, trace = generate('unused', self.payload, {}, transport, self.tools)
        self.assertEqual(result, {'ok': True})
        self.assertEqual(seen[1]['contents'][1], message)
        response = seen[1]['contents'][2]['parts'][0]['functionResponse']
        self.assertEqual(response['id'], 'call-1')
        self.assertTrue(response['response']['evidence'])
        self.assertEqual(trace[0]['name'], 'get_monthly_revenue')
        self.assertEqual(self.payload, original)

    def test_unknown_tool_rejected(self):
        def transport(*args):
            return {'candidates': [{'content': {'parts': [{'functionCall': {'name': 'read_file', 'args': {}}}]}}]}
        with self.assertRaises(ValueError):
            generate('unused', self.payload, {}, transport, self.tools)

    def test_round_budget(self):
        count = []
        def transport(*args):
            count.append(1)
            return {'candidates': [{'content': {'parts': [{'functionCall': {'name': 'get_monthly_revenue', 'args': {}}}]}}]}
        with self.assertRaisesRegex(ValueError, 'round budget'):
            generate('unused', self.payload, {}, transport, self.tools)
        self.assertEqual(len(count), 3)

    def test_parallel_call_budget(self):
        def transport(*args):
            return {'candidates': [{'content': {'parts': [{'functionCall': {'name': 'get_monthly_revenue', 'args': {}}}]*9}}]}
        with self.assertRaisesRegex(ValueError, 'call budget'):
            generate('unused', self.payload, {}, transport, self.tools)

    def test_arguments_rejected(self):
        def transport(*args):
            return {'candidates': [{'content': {'parts': [{'functionCall': {'name': 'get_monthly_revenue', 'args': {'month': 'invalid'}}}]}}]}
        with self.assertRaises(ValueError):
            generate('unused', self.payload, {}, transport, self.tools)
