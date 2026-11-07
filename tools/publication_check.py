"""Check tracked history for accidental private material before publication."""
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
patterns={
 'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'github_token':r'gh[pousr]_[A-Za-z0-9]{30,}',
 'google_api_key':r'AIza[0-9A-Za-z_-]{30,}',
 'personal_email':r'[A-Za-z0-9._%+-]+@(?:gmail\.com|srmist\.edu\.in)',
 'personal_id':r'RA[0-9]{13}',
 'absolute_home_path':r'/Users/[^/\s]+/',
}
findings=[]
objects=subprocess.check_output(['git','rev-list','--objects','--all'],cwd=ROOT,text=True).splitlines()
count=0
for entry in objects:
 sha,_,name=entry.partition(' ')
 if subprocess.check_output(['git','cat-file','-t',sha],cwd=ROOT,text=True).strip()!='blob':continue
 count+=1
 content=subprocess.check_output(['git','cat-file','blob',sha],cwd=ROOT).decode('utf-8',errors='replace')
 for label,pattern in patterns.items():
  if re.search(pattern,content):
   if name == 'tools/publication_check.py' and label == 'absolute_home_path' and content.count('/Users/') == 1 and "r'/Users/[^/\\s]+/'" in content:
    continue  # The scanner's literal detection regex, not a real user path.
   findings.append({'file':name,'kind':label,'object':sha})
report={'history_blobs_scanned':count,'findings':findings,'passed':not findings,'scope':'Pattern scan only, not proof that all sensitive data is absent.'}
(ROOT/'results/publication_check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
raise SystemExit(bool(findings))
