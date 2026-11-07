"""Fail publication when the built static directory contains non-public artifacts."""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
dist=ROOT/'web/dist'
if not (dist/'index.html').exists():raise SystemExit('Build missing')
findings=[]
for p in dist.rglob('*'):
 if not p.is_file():continue
 relative=str(p.relative_to(dist))
 if p.suffix in ('.csv','.sqlite','.db','.zip','.py') or p.name.startswith('.env'):
  findings.append({'path':relative,'reason':'forbidden artifact'})
 text=p.read_bytes().decode('utf-8',errors='ignore')
 for label,pattern in [('private path',r'/Users/[a-zA-Z][^/]+/'),('secret',r'AIza[A-Za-z0-9_-]{30,}|ghp_[A-Za-z0-9]{30,}'),('personal email',r'[\w.+-]+@(?:gmail\.com|srmist\.edu\.in)'),('customer record',r'Customer 00[1-9]')]:
  if re.search(pattern,text):findings.append({'path':relative,'reason':label})
report={'passed':not findings,'files_checked':sum(p.is_file() for p in dist.rglob('*')),'findings':findings}
(ROOT/'results/build_gate.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
raise SystemExit(bool(findings))
