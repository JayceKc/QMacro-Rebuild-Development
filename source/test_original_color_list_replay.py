from pathlib import Path
import hashlib,importlib.util,json,unittest
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'qmacro_color.py').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
EVIDENCE=ROOT/'outputs/plugin-recovery' if (ROOT/'outputs/plugin-recovery').exists() else ROOT/'verification/fixtures'
MODULE=ROOT/'work/qmacro_color.py' if (ROOT/'work/qmacro_color.py').exists() else ROOT/'qmacro_color.py'
spec=importlib.util.spec_from_file_location('list_color',MODULE);color=importlib.util.module_from_spec(spec);spec.loader.exec_module(color)


class ColorListTests(unittest.TestCase):
    def test_all_92_validated_native_color_lists(self):
        report=json.loads((EVIDENCE/'original-color-list-oracle.json').read_text(encoding='utf-8-sig'))
        self.assertTrue(report['ok'] and report['validated_synthetic_picture_input']);self.assertEqual(len(report['cases']),92)
        for c in report['cases']:
            frame=color.PixelImage(c['width'],c['height'],bytes.fromhex(c['rgb_hex']))
            result=frame.find_color(*c['rect'],c['color'],c['similarity'],c['direction'])
            self.assertEqual(result,(c['return_value'],c['x'],c['y']),(c['color'],c['similarity'],c['rgb_hex'][:6]))

    def test_empty_is_black_not_ignored_or_missing_sdk(self):
        frame=color.PixelImage(2,1,bytes.fromhex('000000934039'))
        self.assertEqual(frame.find_color(0,0,2,1,'934039-050505',1),(1,1,0))
        self.assertEqual(frame.find_color(0,0,2,1,'934039-050505|',1),(1,0,0))
        with self.assertRaises(color.ColorContractError):color.parse_color(None,.9)


if __name__=='__main__':unittest.main()
