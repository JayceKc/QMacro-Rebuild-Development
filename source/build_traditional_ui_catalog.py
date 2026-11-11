"""Normalize all twenty inert UI layouts for the owned Unicode renderer."""
from pathlib import Path,PureWindowsPath
import ctypes,hashlib,json,struct,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/QMacro-Rebuild-Development/data';OUT.mkdir(exist_ok=True)
read=ROOT/'outputs/qmacro-readable-analysis'
groups=json.loads((read/'總清單.json').read_text(encoding='utf-8-sig'))['groups']
mapping={s['container']:(g['module'],g['name']) for g in groups for s in g['sources']}
mapper=ctypes.WinDLL('kernel32').LCMapStringEx
mapper.argtypes=[ctypes.c_wchar_p,ctypes.c_uint,ctypes.c_wchar_p,ctypes.c_int,ctypes.c_wchar_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ssize_t]
mapper.restype=ctypes.c_int


def traditional(text):
    if not text:return text
    output=ctypes.create_unicode_buffer(len(text)*2+1)
    n=mapper('zh-TW',0x04000000,text,len(text),output,len(output),None,None,0)
    if not n:raise ctypes.WinError()
    return output[:n]


def integer(properties,key,default):return properties.get(key,{}).get('i32',default)


def main():
    forms=[];pictures=[]
    for path in sorted((read/'介面資料').glob('*.json')):
        ui=json.loads(path.read_text(encoding='utf-8-sig'));module,name=mapping[ui['container']]
        controls=[]
        for control in ui['controls']:
            p=control['properties'];text=p.get('Text',{}).get('text','');items=p.get('Items',{}).get('items',[])
            item={'name':control['name'],'type':control['type'],'rect':p['Rect']['ltrb'],
               'text':traditional(text),'original_text':text,'items':[traditional(s) for s in items],
               'original_items':items,'selected':integer(p,'Selected',0),'checked':integer(p,'Checked',0),
               'visible':bool(integer(p,'Visible',1)),'enabled':bool(integer(p,'Enable',1)),
               'readonly':bool(integer(p,'ReadOnly',0)),'zorder':integer(p,'ZOrder',0),
               'font_pixels':abs(struct.unpack_from('<i',bytes.fromhex(p['Font']['raw_hex']))[0]) if p.get('Font',{}).get('raw_hex') else 10,
               'text_color':integer(p,'ColorText',0),'back_color':integer(p,'ColorBack',16777215),
               'storage':control['storage']}
            if p.get('Pixels',{}).get('bytes',0)>4:
                stored=ROOT/'outputs/restored-files'/ui['container']/'ui-streams'/control['storage']/'Pixels'
                raw=stored.read_bytes();assert hashlib.sha256(raw).hexdigest()==p['Pixels']['sha256']
                size=struct.unpack_from('<I',raw)[0];assert size==len(raw)-4
                payload=raw[4:];assert payload[:2]==b'BM' and struct.unpack_from('<I',payload,2)[0]==len(payload)
                original_name=p.get('PictureName',{}).get('text') or control['name']+'.bmp'
                filename=original_name if PureWindowsPath(original_name).name==original_name and ':' not in original_name else control['name']+'.bmp'
                relative=Path(ui['container'])/control['storage']/filename
                restored=ROOT/'outputs/restored-ui-pictures'/relative;restored.parent.mkdir(parents=True,exist_ok=True);restored.write_bytes(payload)
                copied=OUT.parent/'ui-pictures'/relative;copied.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(restored,copied)
                item.update(picture_path=(Path('ui-pictures')/relative).as_posix(),original_picture_name=original_name,
                            picture_sha256=hashlib.sha256(payload).hexdigest())
                pictures.append({'container':ui['container'],'storage':control['storage'],'original_name':original_name,
                    'relative_file':relative.as_posix(),'pixels_stream_sha256':p['Pixels']['sha256'],
                    'payload_sha256':item['picture_sha256'],'length_prefix':size,'payload_bytes':len(payload),
                    'pixels_changed':False})
            controls.append(item)
        forms.append({'container':ui['container'],'module':module,'name':name,'controls':controls,
           'source_ui_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    assert len(forms)==20 and sum(len(f['controls']) for f in forms)==276
    result={'schema':1,'forms':forms,'fonts_reconstructed':True,'original_native_executable_required':False,
            'full_program_restored':False,'scope':'All extracted controls and items; wrapper artwork/precise native theme not reconstructed.'}
    target=OUT/'ui-forms.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'outputs/restored-ui-pictures/manifest.json').write_text(json.dumps(pictures,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'forms':len(forms),'controls':sum(len(f['controls']) for f in forms),'restored_pictures':len(pictures),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
