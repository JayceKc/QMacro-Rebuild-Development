"""Execute native pair selection/scrubbing and merge loops in isolated memory.

All restored pair contents below are synthetic. Actual missing operands remain
unknown. Compression/Base64/ZIP and callbacks are outside these CPU regions.
"""
import json,hashlib,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'work/emulation-deps')]
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_ESP,UC_X86_REG_EIP
from recover_qmacro_key_info import restore_records,NEGATE
CODE=(ROOT/'work/qmacro-host-image-current/runner.image-pages.bin').read_bytes()
CTX,RECORD,STACK,PAIRS=0x70000000,0x71000000,0x72000000,0x73000000


def cpu(records,payload=None):
    mu=Uc(UC_ARCH_X86,UC_MODE_32);mu.mem_map(0x400000,(len(CODE)+4095)&~4095);mu.mem_write(0x400000,CODE)
    for at,size in ((CTX,0x1000),(RECORD,(len(records)+4095)//4096*4096+4096),(STACK,0x10000),(PAIRS,0x4000)):mu.mem_map(at,size)
    put=lambda at,value:mu.mem_write(at,struct.pack('<I',value&0xffffffff))
    get=lambda at:struct.unpack('<I',mu.mem_read(at,4))[0]
    mu.mem_write(RECORD,records);put(CTX+0xe4,RECORD);put(CTX+0xe8,len(records)//13);bp=STACK+0x8000
    mu.reg_write(UC_X86_REG_EBP,bp);mu.reg_write(UC_X86_REG_ESP,bp-0x2000)
    stops=[]
    if payload is None:
        mu.reg_write(UC_X86_REG_EDI,CTX);mu.reg_write(UC_X86_REG_EBX,0)
        entry=0x611a5b;bounds={0x611af2:'pairs_ready_before_zip',0x611ada:'empty_selection',0x611aed:'bounds_error'}
    else:
        assert payload and len(payload)%5==0
        mu.mem_write(PAIRS,payload);put(bp-0x148,CTX);put(bp-0x150,PAIRS);mu.reg_write(UC_X86_REG_EBX,len(payload)//5)
        entry=0x60dbb9;bounds={0x60dc3a:'merge_done',0x60dcdc:'bounds_error'}
    def hook(cpu,address,size,user):
        if address in bounds:stops.append(bounds[address]);cpu.emu_stop()
    mu.hook_add(UC_HOOK_CODE,hook)
    mu.emu_start(entry,0x400000,count=2000000,timeout=3000000)
    assert stops and stops[0]!='bounds_error',('Native loop did not reach expected stop',hex(mu.reg_read(UC_X86_REG_EIP)))
    result=bytes(mu.mem_read(RECORD,len(records)))
    if payload is None:
        count=mu.reg_read(UC_X86_REG_ESI);data=bytes(mu.mem_read(bp-0x9d4,count*5))
    else:count=get(bp-0x14c);data=payload[:count*5]
    return result,data,count,stops[0]


def normal(rows):return b''.join(struct.pack('<BiiI',op,loc,arg,flags&0xffffffff) for op,loc,arg,flags in rows)


def verify(label,rows,partial=None):
    source=normal(rows);eligible=[i for i,r in enumerate(rows) if r[3]&1][:500]
    expected=b''.join(struct.pack('<Bi',rows[i][0],rows[i][2]) for i in eligible)
    scrubbed,pairs,count,boundary=cpu(source);assert pairs==expected and count==len(eligible)
    expected_records=bytearray(source)
    for i in eligible:expected_records[i*13]=255;struct.pack_into('<i',expected_records,i*13+5,0)
    assert scrubbed==expected_records
    if partial is not None:pairs=pairs[:partial*5]
    if pairs:
        restored,read,merged,merge_boundary=cpu(scrubbed,pairs)
        assert merged==len(pairs)//5 and merge_boundary=='merge_done'
        decoded=struct.pack('<H',len(rows)).translate(NEGATE)+scrubbed.translate(NEGATE)
        owned,changes=restore_records(decoded,list(struct.iter_unpack('<Bi',pairs)),100000)
        assert owned[2:].translate(NEGATE)==restored
        expected_after=bytearray(scrubbed)
        for i,(op,arg) in zip(eligible,struct.iter_unpack('<Bi',pairs)):
            expected_after[i*13]=op;struct.pack_into('<i',expected_after,i*13+5,arg)
        assert restored==expected_after
        allowed={i*13+j for i in eligible[:merged] for j in (0,5,6,7,8)}
        assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(scrubbed,restored)))
    else:restored=scrubbed;merged=0;changes=[]
    return {'label':label,'record_count':len(rows),'eligible_positions':eligible,'export_count':count,'merge_count':merged,'boundary':boundary,
            'source_records_sha256':hashlib.sha256(source).hexdigest(),'scrubbed_records_sha256':hashlib.sha256(scrubbed).hexdigest(),
            'pair_payload_sha256':hashlib.sha256(pairs).hexdigest(),'native_restored_records_sha256':hashlib.sha256(restored).hexdigest(),
            'owned_restore_matches_native':True,'changed_positions':[c['record'] for c in changes]}


def main():
    cases=[]
    for n in (1,4,17,499,500,501,600):
        rows=[(30,i+1,0,[0,1,2,3,0x80000001][i%5]) for i in range(n)]+[(22,0,0,0)]
        cases.append(verify('mixed-flags-'+str(n),rows))
    cases.append(verify('no-protected-bit',[(30,1,0,2),(22,0,0,0)]))
    cases.append(verify('cap-500',[(30,i,0,1) for i in range(600)]+[(22,0,0,0)]))
    cases.append(verify('partial-three',[(30,i,0,1) for i in range(20)]+[(22,0,0,0)],3))
    shapes=[]
    for path in sorted((ROOT/'outputs/QMacro-Rebuild-Development/programs').glob('[0-9][0-9].json')):
        p=json.loads(path.read_text());rows=[list(r) for r in p['code']];missing=p['missing_records']
        assert [i for i,r in enumerate(rows) if r[3]&1][:500]==missing
        original_shape=normal(rows)
        for i in missing:rows[i][0]=30;rows[i][2]=0  # Owned data, NOT recovered opcode/operand.
        result=verify('original-layout-'+path.stem,rows)
        assert result['scrubbed_records_sha256']==hashlib.sha256(original_shape).hexdigest()
        result['synthetic_pair_contents']=True;result['source_program_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();shapes.append(result)
    report={'ok':True,'image_sha256':hashlib.sha256(CODE).hexdigest(),'selection_entry':'0x611a5b','selection_stop_before_zip':'0x611af2',
        'merge_entry':'0x60dbb9','merge_stop':'0x60dc3a','cases':cases,'original_layout_cases':shapes,'case_count':len(cases)+len(shapes),
        'selection_rule':'first at most 500 records with bit0 of final DWORD set; pair is opcode byte + signed operand DWORD',
        'original_missing_values_recovered':0,'native_script_or_os_calls_executed':False,'synthetic_pairs_only':True,
        'limits':['ZIP/Base64 and external merge data source are not exercised here.',
                  'Real layouts use manufactured opcode30/operand0 only to verify positions and preserved bytes.',
                  'These synthetic pairs must never be presented as recovered original instructions.']}
    (ROOT/'outputs/plugin-recovery/runner-protected-pairs.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'ok':True,'cases':report['case_count'],'real_layouts':len(shapes),'original_values_recovered':0}))


if __name__=='__main__':main()
