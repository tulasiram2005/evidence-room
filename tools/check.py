"""Run actual tests and store counts; fail if any verification fails."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
with contextlib.redirect_stdout(io.StringIO()):
    result=unittest.TextTestRunner(verbosity=2).run(suite)
report={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'passed':result.wasSuccessful()}
(ROOT/'results/test_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
sys.exit(0 if result.wasSuccessful() else 1)
