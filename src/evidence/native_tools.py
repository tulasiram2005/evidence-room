"""Bounded Gemini function calling over validated read-only aggregate tools."""
import copy
import json
from .ai_tools import schemas


def generate(url, payload, headers, transport, evidence_tools, max_rounds=3, max_calls=8):
    request = copy.deepcopy(payload)
    request['generationConfig'].pop('responseMimeType', None)
    request['tools'] = [{'functionDeclarations': schemas()}]
    trace = []
    for _ in range(max_rounds):
        reply = transport(url, request, headers)
        content = reply['candidates'][0]['content']
        parts = content['parts']
        calls = [part['functionCall'] for part in parts if 'functionCall' in part]
        if not calls:
            return json.loads(''.join(part.get('text', '') for part in parts)), trace
        if len(trace) + len(calls) > max_calls:
            raise ValueError('Tool call budget exhausted')
        responses = []
        for call in calls:
            name, arguments = call['name'], call.get('args', {})
            values = evidence_tools.call(name, arguments)
            # EvidenceTools rejects unknown names, malformed args and raw-data access.
            response = {'name': name, 'response': {'evidence': values}}
            if 'id' in call:
                response['id'] = call['id']
            responses.append({'functionResponse': response})
            trace.append({'name': name, 'arguments': arguments,
                          'evidence_ids': [value['evidence_id'] for value in values]})
        # Preserve the complete model message, including any thought signatures.
        request['contents'].append(content)
        request['contents'].append({'role': 'user', 'parts': responses})
    raise ValueError('Tool round budget exhausted')
