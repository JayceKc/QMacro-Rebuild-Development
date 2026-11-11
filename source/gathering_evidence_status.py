"""Check saved body evidence without executing original code or trusting a flag."""
import json,hashlib
from pathlib import Path


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def verification(project,kind,actions,case_file,count):
    report=project/('verification/gathering-'+kind+'-original-vs-rebuild.json')
    native=project/('verification/original-gathering-'+kind+'.json')
    if not report.exists() or not native.exists():return False
    d=json.loads(report.read_text())
    action_sha=hashlib.sha256(json.dumps(actions,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
    if not(d.get('ok') is True and d.get('cases')==count and d.get('source_action_sha256')==action_sha and d.get('source_program_sha256')==digest(project/'programs/08.json')
           and d.get('case_spec_sha256')==digest(project/'data'/case_file) and d.get('original_guest_sha256')==digest(native)):return False
    source=Path(__file__).resolve().parent
    expected={'qmacro_gathering_worker.py','replay_gathering_worker.py'} if kind=='worker' else {'qmacro_gathering_routines.py','qmacro_fishing.py','qmacro_gathering_walk.py','replay_gathering_routines.py'}
    return set(d.get('owned_source_sha256',{}))==expected and all(digest(source/n)==sha for n,sha in d['owned_source_sha256'].items())
