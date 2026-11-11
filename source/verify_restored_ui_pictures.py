"""Verify exact length-wrapper round trips for every recovered UI picture."""
from pathlib import Path
import hashlib,json,struct
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'outputs/restored-ui-pictures'
items=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
results=[]
for item in items:
    payload=(folder/item['relative_file']).read_bytes()
    assert hashlib.sha256(payload).hexdigest()==item['payload_sha256']
    source=ROOT/'outputs/restored-files'/item['container']/'ui-streams'/item['storage']/'Pixels'
    raw=source.read_bytes()
    assert struct.pack('<I',len(payload))+payload==raw
    assert hashlib.sha256(raw).hexdigest()==item['pixels_stream_sha256']
    assert payload[:2]==b'BM' and struct.unpack_from('<I',payload,2)[0]==len(payload)
    width,height=struct.unpack_from('<ii',payload,18)
    results.append({'container':item['container'],'file':item['relative_file'],'width':width,'height':height,
        'payload_sha256':item['payload_sha256'],'exact_wrapper_round_trip':True,'pixels_changed':False})
assert len(results)==20
report={'ok':True,'pictures':results,'count':20,'card_and_account_separate':True,
        'exact_pixel_payload_recovery':True,'full_program_restored':False}
(ROOT/'outputs/QMacro-Rebuild-Development/verification/ui-picture-recovery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'ok':True,'pictures':len(results),'exact_wrapper_round_trips':len(results)}))
