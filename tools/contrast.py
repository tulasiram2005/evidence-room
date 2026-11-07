"""Measure configured text/control pairs using WCAG relative luminance."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def luminance(color):
    values=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    values=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
    return sum(a*b for a,b in zip(values,(0.2126,0.7152,0.0722)))
pairs=[]
for theme,colors in {
 'light':{'canvas':'#f2efe6','surface':'#fbf9f3','ink':'#121316','muted':'#4a4d55','blue':'#2447f5','red':'#b52d18'},
 'dark':{'canvas':'#0c0d10','surface':'#14161b','ink':'#ece8dc','muted':'#b6b8b0','blue':'#95a9ff','red':'#ff9078'},
}.items():
 for background in ('canvas','surface'):
  for foreground in ('ink','muted','blue','red'):
   a,b=sorted((luminance(colors[foreground]),luminance(colors[background])))
   ratio=(b+.05)/(a+.05)
   pairs.append({'theme':theme,'foreground':foreground,'background':background,'ratio':round(ratio,3),'aa_normal_text':ratio>=4.5})
a,b=sorted((luminance('#121316'),luminance('#d6ff3d')))
pairs.append({'theme':'both','foreground':'highlight_ink','background':'highlight','ratio':round((b+.05)/(a+.05),3),'aa_normal_text':(b+.05)/(a+.05)>=4.5})
result={'formula':'WCAG relative luminance; 4.5:1 threshold for normal text','pairs':pairs,'passed':all(p['aa_normal_text'] for p in pairs),'scope':'Configured token pairs; does not replace rendered axe checks.'}
(ROOT/'results/contrast.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'pairs':len(pairs),'passed':result['passed']}))
raise SystemExit(not result['passed'])
