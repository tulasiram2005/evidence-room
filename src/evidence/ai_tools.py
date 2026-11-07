"""Read-only, allowlisted aggregate tools. Raw CSV values are never returned."""
import json
import re
from pathlib import Path

MONTHS = ('2026-08', '2026-09')
SPECS = {
    'get_data_health': {},
    'get_monthly_revenue': {'month': {'type': 'string', 'enum': list(MONTHS)}},
    'get_waterfall': {'month': {'type': 'string', 'enum': list(MONTHS)}},
    'get_top_products': {'limit': {'type': 'integer', 'minimum': 1, 'maximum': 10}, 'month': {'type': 'string', 'enum': list(MONTHS)}},
    'get_new_vs_repeat': {'month': {'type': 'string', 'enum': list(MONTHS)}},
    'get_exclusions': {'reason_code': {'type': 'string', 'pattern': '^[A-Z_]+$'}},
    'get_sensitivity': {'scenario_id': {'type': 'string'}},
    'get_flip_analysis': {},
}

def schemas():
    return [{'name': name, 'description': 'Read computed aggregate evidence only.',
             'parameters': {'type': 'object', 'properties': properties,
                            'additionalProperties': False,
                            'required': ['month'] if name == 'get_waterfall' else ['limit'] if name == 'get_top_products' else []}}
            for name, properties in SPECS.items()]

class EvidenceTools:
    def __init__(self, root):
        self.root = Path(root)

    def call(self, name, arguments):
        if name not in SPECS or type(arguments) is not dict:
            raise ValueError('Unknown tool or invalid arguments')
        spec = next(item['parameters'] for item in schemas() if item['name'] == name)
        if set(arguments) - set(spec['properties']) or set(spec['required']) - set(arguments):
            raise ValueError('Unexpected or missing arguments')
        for key, value in arguments.items():
            rule = spec['properties'][key]
            if rule['type'] == 'integer':
                if type(value) is not int or not rule['minimum'] <= value <= rule['maximum']:
                    raise ValueError('Invalid limit')
            elif type(value) is not str or len(value) > 100:
                raise ValueError('Invalid string argument')
            if 'enum' in rule and value not in rule['enum']:
                raise ValueError('Invalid month')
            if 'pattern' in rule and not re.fullmatch(rule['pattern'], value):
                raise ValueError('Invalid reason code')
        file, pointer = {
            'get_data_health': ('data_health', ''),
            'get_monthly_revenue': ('kpis', '/monthly'),
            'get_waterfall': ('waterfall', ''),
            'get_top_products': ('kpis', '/monthly_products' if 'month' in arguments else '/top_products'),
            'get_new_vs_repeat': ('kpis', '/cohorts'),
            'get_exclusions': ('kpis', '/exclusions'),
            'get_sensitivity': ('sensitivity', ''),
            'get_flip_analysis': ('flip', ''),
        }[name]
        data = json.loads((self.root / 'results' / (file + '.json')).read_text())
        if pointer:
            data = data[pointer[1:]]
        items = []
        if name == 'get_waterfall':
            key = arguments['month']
            items = [(pointer + '/' + key, data[key])]
        elif isinstance(data, list):
            for index, value in enumerate(data):
                if 'month' in arguments and value.get('order_month') != arguments['month']:
                    continue
                if 'reason_code' in arguments and value.get('reason_code') != arguments['reason_code']:
                    continue
                if 'scenario_id' in arguments and value.get('id') != arguments['scenario_id']:
                    continue
                # Product names are untrusted CSV text: only identifiers/rank and numbers go to AI.
                if name == 'get_top_products':
                    value = {k: v for k, v in value.items() if k in ('revenue_paise', 'rank', 'order_month')}
                items.append((pointer + '/' + str(index), value))
            if 'limit' in arguments:
                items = items[:arguments['limit']]
        else:
            if name == 'get_data_health':
                data = {table: {key: value for key, value in stats.items() if key in ('rows', 'invalid_dates', 'repeated_key_groups')} for table, stats in data.items()}
            items = [(pointer, data)]
        return [{'evidence_id': file + '#' + path, 'source_file': 'results/' + file + '.json',
                 'pointer': path, 'value': value} for path, value in items]
