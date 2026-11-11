"""Meaningful format/integrity checks with synthetic, encrypted sidecar fixtures."""
import base64
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
import zlib
from recover_qmacro_key_info import NEGATE,decode_key_info,decode_message,restore_records

def fixture(payload,password=b'!',name=b'1'):
    # Independent stdlib ZIP reader must accept the resulting traditional encrypted ZIP.
    crc=zlib.crc32(payload)&0xffffffff
    compressor=zlib.compressobj(wbits=-15)
    compressed=compressor.compress(payload)+compressor.flush()
    keys=[0x12345678,0x23456789,0x34567890]
    def crc_entry(value):
        for _ in range(8):value=(value>>1)^(0xedb88320 if value&1 else 0)
        return value
    table=list(map(crc_entry,range(256)))
    def update(byte):
        keys[0]=(keys[0]>>8)^table[(keys[0]^byte)&255]
        keys[1]=((keys[1]+(keys[0]&255))*134775813+1)&0xffffffff
        keys[2]=(keys[2]>>8)^table[(keys[2]^(keys[1]>>24))&255]
    for byte in password:update(byte)
    encrypted=bytearray()
    for byte in bytes(11)+bytes([crc>>24])+compressed:
        temp=keys[2]|2
        encrypted.append(byte^((temp*(temp^1)>>8)&255))
        update(byte)
    local=struct.pack('<4s5H3I2H',b'PK\x03\x04',20,1,8,0,33,crc,len(encrypted),len(payload),len(name),0)+name+encrypted
    central=struct.pack('<4s6H3I5H2I',b'PK\x01\x02',20,20,1,8,0,33,crc,len(encrypted),len(payload),len(name),0,0,0,0,0,0)+name
    return local+central+struct.pack('<4s4H2IH',b'PK\x05\x06',0,0,1,1,len(central),len(local),0)

def script():
    records=[(30,0,0,0),(255,1,0,1),(35,2,0,0),(255,3,0,1),(255,4,0,1),(22,0,0,0)]
    normal=b''.join(struct.pack('<Biii',*x) for x in records)
    return struct.pack('<H',len(records)).translate(NEGATE)+normal.translate(NEGATE)


def varint(value):
    encoded = bytearray()
    while value >= 128:
        encoded.append((value & 127) | 128)
        value >>= 7
    return bytes(encoded) + bytes([value])


def field(number, data):
    return varint(number << 3 | 2) + varint(len(data)) + data


class MessageTests(unittest.TestCase):
    macro = b'synthetic-macro\x83'
    pairs = [(30, 61), (4, 85), (6, 1)]
    sidecar = base64.b64encode(fixture(b''.join(struct.pack('<Bi', *p) for p in pairs)))

    def merge_message(self):
        return field(2, self.sidecar) + b'\x18\x7f' + field(1, self.macro)

    def add_message(self, sidecar):
        run_data = field(2, b'synthetic-shm') + b'\x28\x01' + field(3, sidecar)
        macro_info = b'\x08\x01' + field(15, self.macro)
        return field(2, macro_info) + field(1, run_data)

    def test_merge_message_in_either_field_order(self):
        for message in (self.merge_message(), field(1, self.macro) + field(2, self.sidecar)):
            pairs, report = decode_message(message, 'merge-message', self.macro)
            self.assertEqual(pairs, self.pairs)
            self.assertEqual(report['macro_id_hex'], self.macro.hex())
            self.assertTrue(report['macro_id_matches_expected'])
            self.assertEqual(report['sidecar_field'], '_MergeScriptKeyInfo_R.key_info')

    def test_nested_add_macro(self):
        pairs, report = decode_message(self.add_message(self.sidecar), 'add-message', self.macro)
        self.assertEqual(pairs, self.pairs)
        self.assertEqual(report['sidecar_field'], '_AddMacro_R.macro_run_data.merge_part')

    def test_different_or_missing_id_is_rejected(self):
        for message, format in (
            (self.merge_message(), 'merge-message'),
            (self.add_message(self.sidecar), 'add-message'),
            (field(1, field(3, self.sidecar)), 'add-message'),
        ):
            with self.subTest(format=format), self.assertRaisesRegex(ValueError, 'macro ID'):
                decode_message(message, format, b'other')

    def test_empty_and_sentinel_add_macro(self):
        for value in (b'', b'none'):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'no instruction sidecar'):
                decode_message(self.add_message(value), 'add-message', self.macro)

    def test_malformed_wire_and_duplicate_fields(self):
        for suffix in (b'\x0a\x02x', b'\x08\x00', b'\x00', b'\x1a'+b'\xff'*10,
                       field(2, self.sidecar)):
            with self.subTest(suffix=suffix[:8]), self.assertRaises(ValueError):
                decode_message(self.merge_message() + suffix, 'merge-message', self.macro)
        duplicate_info = field(2, field(15, self.macro) * 2) + field(1, field(3, self.sidecar))
        with self.assertRaisesRegex(ValueError, 'duplicate Protobuf field 15'):
            decode_message(duplicate_info, 'add-message', self.macro)

    def test_raw_zip_and_embedded_nul_are_not_runner_message_text(self):
        for value in (base64.b64decode(self.sidecar), self.sidecar + b'\0extra'):
            with self.subTest(value=value[:8]), self.assertRaisesRegex(ValueError, 'Base64 text'):
                decode_message(field(1, self.macro) + field(2, value), 'merge-message', self.macro)

    def test_cli_does_not_write_before_association_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            message = folder / 'message.pb'
            message.write_bytes(self.add_message(self.sidecar))
            decoded = folder / 'Script.decoded'
            decoded.write_bytes(script())
            output = folder / 'result'
            args = [sys.executable, str(Path(__file__).with_name('recover_qmacro_key_info.py')),
                    str(message), '--input-format', 'add-message', '--script-decoded', str(decoded),
                    '--expected-script-sha256', hashlib.sha256(script()).hexdigest(),
                    '--output-directory', str(output)]
            for extra in ([], ['--expected-macro-id-hex', '00']):
                result = subprocess.run(args + extra, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())
            subprocess.run(args + ['--expected-macro-id-hex', self.macro.hex()], check=True, capture_output=True)
            candidate, changes = restore_records(script(), self.pairs)
            self.assertEqual((output / 'Script.restored-candidate.decoded.bin').read_bytes(), candidate)
            self.assertEqual(json.loads((output / 'key-info.json').read_text())['changes'], changes)


class KeyInfoTests(unittest.TestCase):
    def test_encrypted_base64_round_trip_and_preserved_fields(self):
        pairs=[(30,61),(4,85),(6,1)]
        blob=fixture(b''.join(struct.pack('<Bi',*x) for x in pairs))
        decoded,report=decode_key_info(base64.encodebytes(blob))
        self.assertEqual(decoded,pairs)
        self.assertEqual(report['records'],3)
        before=script();after,changes=restore_records(before,pairs,100)
        self.assertEqual([x['record'] for x in changes],[1,3,4])
        allowed={2+i*13+j for i in [1,3,4] for j in [0,5,6,7,8]}
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after))))
    def test_bad_password_rejected(self):
        with self.assertRaises(ValueError):decode_key_info(fixture(struct.pack('<Bi',30,61),password=b'wrong'))
    def test_corruption_rejected(self):
        blob=bytearray(fixture(struct.pack('<Bi',30,61)));blob[43]^=1
        with self.assertRaises(ValueError):decode_key_info(bytes(blob))
    def test_bad_member_name_rejected(self):
        with self.assertRaises(ValueError):decode_key_info(fixture(struct.pack('<Bi',30,61),name=b'2'))
    def test_partial_pair_rejected(self):
        with self.assertRaises(ValueError):decode_key_info(fixture(bytes(6)))
    def test_wrong_target_rejected(self):
        restored,_=restore_records(script(),[(30,61)],100)
        with self.assertRaises(ValueError):restore_records(restored,[(30,61)],100)
    def test_bad_branch_rejected(self):
        with self.assertRaises(ValueError):restore_records(script(),[(6,1000)],100)
    def test_bad_string_rejected(self):
        with self.assertRaises(ValueError):restore_records(script(),[(30,1000)],100)
    def test_branch_exactly_one_past_code_end_rejected(self):
        # Native control-handler evidence rejects target == record_count.
        for opcode,operand in ((5,6),(12,6),(6,5),(16,5)):
            with self.subTest(opcode=opcode):
                with self.assertRaises(ValueError):restore_records(script(),[(opcode,operand)],100)
    def test_header_count_must_match_full_record_stream(self):
        source=script()
        for count in (0,5,7):
            bad=struct.pack('<H',count).translate(NEGATE)+source[2:]
            with self.subTest(count=count):
                with self.assertRaises(ValueError):restore_records(bad,[(30,61)],100)

if __name__=='__main__':unittest.main()
