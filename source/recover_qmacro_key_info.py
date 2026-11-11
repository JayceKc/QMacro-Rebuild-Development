"""Inspect/restore QMacro's protected instruction sidecar. Never runs target code."""
from pathlib import Path
import argparse
import base64
import binascii
import hashlib
import io
import json
import struct
import zipfile
import zlib

NEGATE = bytes((-x)&255 for x in range(256))
STRING_OPS = {2,4,27,28,30,31,37,38}
MESSAGE_LIMIT = 2 * 1024 * 1024


def read_varint(data, cursor):
    value = 0
    for shift in range(0, 70, 7):
        if cursor >= len(data):
            raise ValueError('Truncated Protobuf varint')
        byte = data[cursor]
        cursor += 1
        if shift == 63 and byte > 1:
            raise ValueError('Protobuf varint exceeds 64 bits')
        value |= (byte & 0x7f) << shift
        if byte < 0x80:
            return value, cursor


def read_bytes_fields(data, wanted):
    """Read selected singular bytes/message fields from the recovered proto2 schema."""
    if len(data) > MESSAGE_LIMIT:
        raise ValueError('Protobuf payload exceeds offline inspection limit')
    values = {}
    cursor = 0
    while cursor < len(data):
        tag, cursor = read_varint(data, cursor)
        field, wire = tag >> 3, tag & 7
        if not 1 <= field < 1 << 29:
            raise ValueError('Invalid Protobuf field number')
        if field in wanted and (wire != 2 or field in values):
            raise ValueError(f'Unexpected wire type or duplicate Protobuf field {field}')
        if wire == 0:
            _, cursor = read_varint(data, cursor)
            continue
        if wire == 2:
            size, cursor = read_varint(data, cursor)
        elif wire in (1, 5):
            size = 8 if wire == 1 else 4
        else:
            raise ValueError(f'Unsupported Protobuf wire type {wire}')
        end = cursor + size
        if end > len(data):
            raise ValueError('Truncated Protobuf field')
        if field in wanted:
            values[field] = data[cursor:end]
        cursor = end
    return values


def decode_message(data, message_type, expected_macro_id=None):
    fields = read_bytes_fields(data, {1, 2})
    if message_type == 'merge-message':
        macro_id, sidecar = fields.get(1), fields.get(2)
        sidecar_field = '_MergeScriptKeyInfo_R.key_info'
    elif message_type == 'add-message':
        run_data = read_bytes_fields(fields.get(1, b''), {3})
        macro_info = read_bytes_fields(fields.get(2, b''), {15})
        macro_id, sidecar = macro_info.get(15), run_data.get(3)
        sidecar_field = '_AddMacro_R.macro_run_data.merge_part'
    else:
        raise ValueError('Unknown QMacro message type')
    if expected_macro_id is not None and macro_id != expected_macro_id:
        raise ValueError('Protobuf macro ID differs from the expected bytes')
    if not sidecar or sidecar == b'none':
        raise ValueError(f'{sidecar_field} has no instruction sidecar')
    if sidecar.startswith(b'PK\x03\x04') or b'\0' in sidecar:
        raise ValueError('Expected Base64 text in the Runner message')
    pairs, report = decode_key_info(sidecar)
    report.update(
        source_format=message_type,
        sidecar_field=sidecar_field,
        macro_id_hex=macro_id.hex() if macro_id is not None else None,
        macro_id_matches_expected=expected_macro_id is not None,
        message_sha256=hashlib.sha256(data).hexdigest(),
    )
    return pairs, report

def decode_key_info(data):
    if data.startswith(b'PK\x03\x04'):
        archive = data
    else:
        try:
            archive = base64.b64decode(b''.join(data.split()), validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError('Expected Base64 ZIP or raw ZIP sidecar') from exc
    if len(archive)>1024*1024:
        raise ValueError('Oversized sidecar archive')
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            members = z.infolist()
            if len(members)!=1 or members[0].filename!='1':
                raise ValueError('Expected one ZIP member named 1')
            entry = members[0]
            if not 0 < entry.file_size <= 500*5 or entry.file_size%5:
                raise ValueError('Expected 1..500 five-byte instruction pairs')
            payload = z.read(entry, pwd=b'!')  # Read validates full ZIP CRC and size.
            if len(payload)!=entry.file_size:
                raise ValueError('Sidecar size mismatch')
            crc = entry.CRC
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError, zlib.error) as exc:
        raise ValueError('Sidecar ZIP decryption/integrity failed: '+str(exc)) from exc
    pairs = list(struct.iter_unpack('<Bi',payload))
    if any(opcode not in range(2,41) and opcode!=255 for opcode,operand in pairs):
        raise ValueError('Sidecar contains unsupported instruction tags')
    return pairs, dict(records=len(pairs), zip_crc32=f'{crc:08x}',
                       zip_sha256=hashlib.sha256(archive).hexdigest(),
                       payload_sha256=hashlib.sha256(payload).hexdigest())

def restore_records(decoded_script,pairs,string_count=None):
    # The input is the Blowfish-decoded Script stream, before per-byte negation.
    terminal = b'\xea'+bytes(12)
    if len(decoded_script)<2:
        raise ValueError('Decoded Script header is missing')
    total=struct.unpack('<H',decoded_script[:2].translate(NEGATE))[0]
    end=2+total*13
    if not total or end>len(decoded_script) or len(decoded_script)-end>8 or decoded_script[end-13:end]!=terminal:
        raise ValueError('Invalid decoded Script terminator/tail')
    normal=bytearray(decoded_script[2:end].translate(NEGATE))
    eligible=[i for i in range(total) if normal[i*13+9]&1][:len(pairs)]
    if len(eligible)!=len(pairs):
        raise ValueError('Not enough protected instruction positions')
    changed=[]
    for index,(opcode,operand) in zip(eligible,pairs):
        offset=index*13
        if normal[offset]!=255 or struct.unpack_from('<i',normal,offset+5)[0]!=0:
            raise ValueError(f'Target record {index} is not a protected empty slot')
        if opcode in STRING_OPS and string_count is not None and not 0<=operand<string_count:
            raise ValueError(f'String index out of range at record {index}')
        if opcode in {5,12} and not 0<=operand<total:
            raise ValueError(f'Absolute branch out of range at record {index}')
        if opcode in {6,16} and not 0<=index+operand<total:
            raise ValueError(f'Relative branch out of range at record {index}')
        if opcode==24 and not 0<=index+operand<=total:
            raise ValueError(f'Worker entry out of range at record {index}')
        normal[offset]=opcode
        struct.pack_into('<i',normal,offset+5,operand)
        changed.append(dict(record=index,opcode=opcode,operand=operand))
    # Only opcode and operand are changed; original location, flags and padding survive.
    output=decoded_script[:2]+bytes(normal).translate(NEGATE)+decoded_script[end:]
    assert len(output)==len(decoded_script)
    return output,changed

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('key_info',type=Path)
    parser.add_argument('--input-format',choices=('sidecar','merge-message','add-message'),default='sidecar',
                        help='Message formats expect only the already decrypted Protobuf payload')
    parser.add_argument('--expected-macro-id-hex',help='Exact macro ID bytes, in hexadecimal')
    parser.add_argument('--script-decoded',type=Path)
    parser.add_argument('--expected-script-sha256')
    parser.add_argument('--string-count',type=int)
    parser.add_argument('--output-directory',type=Path,required=True)
    args=parser.parse_args()
    expected_macro_id = None
    if args.expected_macro_id_hex is not None:
        try:
            expected_macro_id = bytes.fromhex(args.expected_macro_id_hex)
        except ValueError:
            parser.error('--expected-macro-id-hex must contain hexadecimal bytes')
        if not expected_macro_id or args.input_format == 'sidecar':
            parser.error('--expected-macro-id-hex requires a nonempty ID and a message format')
    if args.input_format == 'sidecar':
        pairs,report=decode_key_info(args.key_info.read_bytes())
    else:
        if args.script_decoded and expected_macro_id is None:
            parser.error('--expected-macro-id-hex is required when restoring from a message')
        with args.key_info.open('rb') as payload:
            pairs,report=decode_message(payload.read(MESSAGE_LIMIT + 1),args.input_format,expected_macro_id)
    report.update(key_info=str(args.key_info.resolve()),
        limitations=['ZIP integrity does not cryptographically bind this sidecar to a macro ID.',
                     'Caller must establish the correct module/key_info association.',
                     'Output is an offline candidate, never installed or executed.',
                     'Runtime-only operand bounds are not all verified here.'])
    result=None
    if args.script_decoded:
        if not args.expected_script_sha256:
            parser.error('--expected-script-sha256 is required for restoration')
        original=args.script_decoded.read_bytes()
        actual=hashlib.sha256(original).hexdigest()
        if actual!=args.expected_script_sha256.lower():
            raise ValueError('Input decoded Script hash mismatch')
        result,changes=restore_records(original,pairs,args.string_count)
        report.update(script=str(args.script_decoded.resolve()),input_sha256=actual,
                      output_sha256=hashlib.sha256(result).hexdigest(),changes=changes,
                      module_association=('message ID matches caller-supplied bytes; source association not authenticated'
                                          if expected_macro_id is not None
                                          else 'caller-supplied; not validated by sidecar CRC'))
    args.output_directory.mkdir(parents=True,exist_ok=False)
    if result is not None:
        (args.output_directory/'Script.restored-candidate.decoded.bin').write_bytes(result)
    (args.output_directory/'key-info.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (args.output_directory/'instruction-pairs.json').write_text(json.dumps(pairs),encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':
    main()
