"""Optional bounded provider transport. Core analysis never invokes this module."""
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from .ai_tools import EvidenceTools
from .verify import verify

class ProviderFailure(Exception):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProviderFailure('Provider redirect refused')

def post(url, payload, headers, attempts=3):
    if not (url.startswith('https://generativelanguage.googleapis.com/v1beta/models/') or url == 'http://127.0.0.1:11434/api/chat'):
        raise ProviderFailure('Unapproved provider destination')
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'Content-Type':'application/json', **headers}, method='POST')
            with opener.open(request, timeout=15) as response:
                data = response.read(1_000_001)
                if len(data)>1_000_000: raise ProviderFailure('Response too large')
                return json.loads(data)
        except urllib.error.HTTPError as error:
            if error.code not in (429,500,502,503,504) or attempt == attempts-1:
                raise ProviderFailure('Provider HTTP failure: '+str(error.code)) from None
            time.sleep(2**attempt)
        except (urllib.error.URLError, TimeoutError, ValueError):
            raise ProviderFailure('Provider unavailable or invalid JSON') from None
    raise ProviderFailure('Retries exhausted')

def draft(root, *, allow_gemini=False, allow_ollama=False, transport=post):
    tools = EvidenceTools(root)
    monthly = tools.call('get_monthly_revenue', {})
    baseline = json.loads((root/'results/ai_claims.json').read_text())
    evidence = json.loads((root/'results/evidence.json').read_text())
    prompt = ('Return JSON using exactly this schema/example, supported by the aggregate evidence. '
              'Do not infer causes or lifetime tenure. Use only the two allowed factual sentences. '
              +json.dumps({'example':baseline, 'aggregate_tool_results':monthly, 'evidence':evidence},sort_keys=True))
    fingerprint = hashlib.sha256(prompt.encode()).hexdigest()
    cache = root/'results/provider_run.json'
    configuration = {'gemini':allow_gemini,'ollama':allow_ollama,'gemini_model':os.getenv('GEMINI_MODEL'), 'ollama_model':os.getenv('OLLAMA_MODEL')}
    if cache.exists():
        previous=json.loads(cache.read_text())
        if previous.get('prompt_hash')==fingerprint and previous.get('configuration')==configuration and previous.get('provider')!='deterministic_mock':
            verify(previous['response'],evidence)
            return previous
    failures=[]
    candidates=[]
    if allow_gemini:
        model=os.getenv('GEMINI_MODEL','')
        if os.getenv('GEMINI_FREE_TIER_CONFIRMED')!='yes' or not os.getenv('GEMINI_API_KEY') or not re.fullmatch(r'gemini-[a-zA-Z0-9.-]*flash[a-zA-Z0-9.-]*',model):
            failures.append({'provider':'gemini','reason':'Free-tier confirmation, Flash model or key missing'})
        else:
            candidates.append(('gemini',model,'https://generativelanguage.googleapis.com/v1beta/models/'+model+':generateContent',{'contents':[{'role':'user','parts':[{'text':prompt}]}],'generationConfig':{'responseMimeType':'application/json','temperature':0,'maxOutputTokens':1800}}, {'x-goog-api-key':os.environ['GEMINI_API_KEY']}))
    if allow_ollama:
        model=os.getenv('OLLAMA_MODEL','')
        if model and re.fullmatch(r'[a-zA-Z0-9_.:/-]+',model):
            candidates.append(('ollama',model,'http://127.0.0.1:11434/api/chat',{'model':model,'messages':[{'role':'user','content':prompt}],'stream':False,'format':'json','options':{'temperature':0,'num_predict':1800}},{}))
        else: failures.append({'provider':'ollama','reason':'Local model not configured'})
    provider, model, response='deterministic_mock',None,baseline
    for name, model_name, url, payload, headers in candidates:
        try:
            reply=transport(url,payload,headers)
            content=''.join(p.get('text','') for p in reply['candidates'][0]['content']['parts']) if name=='gemini' else reply['message']['content']
            candidate=json.loads(content)
            checks=verify(candidate,evidence)
            if not checks or any(c['verdict']!='verified' for c in checks):
                raise ProviderFailure('Draft failed claim verification')
            provider,model,response=name,model_name,candidate
            break
        except (ProviderFailure,ValueError,KeyError,IndexError,TypeError):
            failures.append({'provider':name,'reason':'Unavailable, malformed or unverified response; fallback used'})
    result={'provider':provider,'model':model,'prompt_hash':fingerprint,'prompt':prompt,'configuration':configuration,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'response':response,'claim_checks':verify(response,evidence),'failures':failures,'mode':'aggregate-grounded JSON; native model-directed tool calls not enabled'}
    cache.write_text(json.dumps(result,indent=2)+'\n')
    return result
