"""Native observation replay, independent of any live game or original DLL."""
import json
from pathlib import Path
import tempfile
import unittest
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from qmacro_color import PixelImage
from qmacro_picture import find_pic,find_pic_files,load_bmp,PictureContractError

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'outputs/plugin-recovery' if (ROOT/'outputs/plugin-recovery').exists() else ROOT/'verification/fixtures'


def pixels(obj):
    return PixelImage(obj['width'], obj['height'], bytes.fromhex(obj['rgb_hex']))


class ImageReplay(unittest.TestCase):
    def test_original_filename_list_empty_and_unavailable_slots(self):
        data=json.loads((EVIDENCE/'original-picture-list-oracle.json').read_text(encoding='utf-8-sig'))
        self.assertTrue(data['ok']);self.assertTrue(data['input_validated']);self.assertEqual(len(data['samples']),11)
        rgb=bytearray([17,34,51]*64)
        for y in range(2,5):
            for x in range(3,6):rgb[(y*8+x)*3:(y*8+x)*3+3]=bytes((145,16,10))
        scene=PixelImage(8,8,rgb);target=PixelImage(3,3,bytes((145,16,10))*9);other=PixelImage(3,3,bytes((204,221,85))*9)
        def resolve(name):
            if name=='target.bmp':return target
            if name=='other.bmp':return other
            raise FileNotFoundError(name)
        for sample in data['samples']:
            self.assertEqual(find_pic_files(scene,(0,0,8,8),'|'.join(sample['tokens']),resolve,'000000',1,0),(sample['return_value'],sample['x'],sample['y']))
    def test_all_native_observations(self):
        count = 0
        for filename in ('original-image-oracle.json', 'original-image-oracle-extended.json'):
            d = json.loads((EVIDENCE/filename).read_text(encoding='utf-8-sig'))
            self.assertTrue(d['ok'])
            self.assertTrue(d['vmware_guest_guard'])
            self.assertTrue(d['output_variants_reset'])
            self.assertEqual(d['version'], '7.2450')
            for s in d['samples']:
                with self.subTest(file=filename, name=s['name'], sim=s['similarity'], delta=s['delta']):
                    self.assertTrue(s['input_validated'])
                    actual = find_pic(pixels(s['scene']), s['rect'], [pixels(t) for t in s['templates']],
                                      s['delta'], s['similarity'], s['direction'])
                    self.assertEqual(actual, (s['return_value'], s['x'], s['y']))
                    count += 1
            self.assertEqual(d['capture']['return_value'], 1)
            self.assertEqual(d['capture']['pixels'], d['capture']['expected'])
        self.assertEqual(count, 141)  # 77 distinct parameter sets; 64 repeated in extension.

    def test_all_original_plain_bmp_assets(self):
        folder = ROOT/'outputs/restored-files/account/01/attachments'
        if not folder.exists():folder=ROOT/'assets/account-01/attachments'
        count = 0
        for path in folder.glob('*.bmp'):
            if path.read_bytes()[:4] == b'DMDM':
                with self.assertRaises(PictureContractError): load_bmp(path)
            else:
                image = load_bmp(path)
                self.assertEqual(len(image.rgb), image.width * image.height * 3)
                count += 1
        self.assertEqual(count, 379)

    def test_reject_invalid_capture_and_cancel(self):
        image = PixelImage(3, 3, bytes([1, 2, 3] * 9))
        with self.assertRaises(PictureContractError):
            find_pic(image, (0, 0, 4, 3), [image], '000000', 1)
        with self.assertRaises(InterruptedError):
            find_pic(image, (0, 0, 3, 3), [image], '000000', 1, cancelled=lambda: True)
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/'bad.bmp'; p.write_bytes(b'BM'+bytes(60))
            with self.assertRaises(PictureContractError): load_bmp(p)

    def test_bmp_padding_channel_order_and_both_row_directions(self):
        # Two pixels need two padding bytes per row. Distinct primaries make
        # orientation/channel swaps observable independently of native matcher.
        top = bytes((0,0,255, 0,255,0, 99,99))
        bottom = bytes((255,0,0, 255,255,255, 88,88))
        expected = bytes((255,0,0, 0,255,0, 0,0,255, 255,255,255))
        with tempfile.TemporaryDirectory() as folder:
            for height, data in ((2, bottom+top), (-2, top+bottom)):
                header = b'BM'+struct.pack('<IHHI',70,0,0,54)
                header += struct.pack('<IiiHHIIiiII',40,2,height,1,24,0,16,0,0,0,0)
                path=Path(folder)/'fixture.bmp';path.write_bytes(header+data)
                self.assertEqual(load_bmp(path).rgb, expected)


if __name__ == '__main__': unittest.main()
