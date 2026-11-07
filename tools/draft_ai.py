"""Opt-in provider validation; does not modify deterministic submission results."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.evidence.providers import draft
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--gemini',action='store_true')
parser.add_argument('--ollama',action='store_true')
args=parser.parse_args()
result=draft(ROOT,allow_gemini=args.gemini,allow_ollama=args.ollama)
print('Actual provider:',result['provider'])
print('Saved privately: results/provider_run.json')
