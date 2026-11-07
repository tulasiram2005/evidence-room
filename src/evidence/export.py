"""Allowlisted static-site payload; never ship raw or clean order files."""
import json
from .pipeline import write_json

def export(root, rows):
    names = ['data_health', 'decisions', 'kpis', 'waterfall', 'sensitivity', 'flip', 'claim_checks', 'evidence']
    payload = {name: json.loads((root/'results'/f'{name}.json').read_text()) for name in names}
    payload['summary'] = (root/'executive_summary.md').read_text()
    payload['rejections'] = [{key: r[key] for key in ('source_row_number', 'bucket', 'reason_code', 'order_month', 'currency', 'face_value')} for r in rows if r['bucket'] == 'rejected']
    target = root/'web/src'
    target.mkdir(parents=True, exist_ok=True)
    write_json(target/'evidence.json', payload)
