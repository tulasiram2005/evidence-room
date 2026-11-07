"""Package source and evidence for private assessment, never dependencies/secrets."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
allowed={'.py','.md','.csv','.json','.sql','.toml','.yml','.yaml','.tsx','.css','.html','.mjs','.svg'}
output=ROOT.parent/'Evidence_Room_Submission.zip'
with ZipFile(output,'w',ZIP_DEFLATED) as archive:
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if not p.is_file() or any(x in rel.parts for x in ('.git','.venv','.venv311','.hypothesis','.ruff_cache','node_modules','__pycache__','dist','.pytest_cache')):continue
        if p.name.startswith('.env') or p.name == 'provider_run.json':continue
        if p.suffix in allowed or p.name in ('Makefile','_headers','.gitignore','requirements-dev.lock'):
            archive.write(p,Path('evidence-room')/rel)
print(output)
print('Bytes:',output.stat().st_size)
