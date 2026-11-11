from pathlib import Path
import importlib.util,json,unittest
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'outputs/plugin-recovery' if (ROOT/'outputs/plugin-recovery').exists() else ROOT/'verification/fixtures'
MODULE=ROOT/'work/qmacro_color.py' if (ROOT/'work/qmacro_color.py').exists() else ROOT/'qmacro_color.py'
spec=importlib.util.spec_from_file_location('qmacro_color',MODULE);color=importlib.util.module_from_spec(spec);spec.loader.exec_module(color)
class NativeColorReplay(unittest.TestCase):
    def test_single_pixel_matches_actual_native_observations(self):
        count=0
        for filename in ('original-color-oracle-valid-157.json','original-color-oracle-boundaries.json'):
            d=json.loads((EVIDENCE/filename).read_text(encoding='utf-8-sig'))
            self.assertTrue(d['ok']);self.assertEqual(d['original_version'],'7.2450')
            for sample in d['samples']:
                self.assertTrue(sample['capture_valid'])
                if 'pixel' not in sample:continue
                with self.subTest(file=filename,case=sample['category'],sim=sample['sim']):
                    n=sample['pixel']&0xffffff;rgb=((n>>16)&255,(n>>8)&255,n&255)
                    match=color.matches_rgb(rgb,color.parse_color(sample['color'],sample['sim']))
                    self.assertEqual(match,sample['x']>=0)
                    self.assertEqual('%02x%02x%02x'%rgb,sample['get_color'])
                    count+=1
        self.assertEqual(count,254)
    def test_rectangle_and_direction_native_fixtures(self):
        filenames=['original-color-oracle-boundaries.json']
        extra=EVIDENCE/'original-color-oracle-ordering.json'
        if extra.exists():filenames.append(extra.name)
        for filename in filenames:
            d=json.loads((EVIDENCE/filename).read_text(encoding='utf-8-sig'))
            for sample in d['samples']:
                if 'query_rect' not in sample:continue
                self.assertTrue(sample['capture_valid'])
                rgb=bytearray([17,34,51]*9)
                for dot in sample['dots']:
                    i=(dot['Y']*3+dot['X'])*3;rgb[i:i+3]=bytes((145,16,10))
                for dot in sample.get('white_dots',[]):
                    i=(dot['Y']*3+dot['X'])*3;rgb[i:i+3]=b'\xff\xff\xff'
                rect=sample['query_rect'];image=color.PixelImage(3,3,rgb,origin=tuple(rect[:2]))
                with self.subTest(file=filename,case=sample['category'],direction=sample['direction']):
                    self.assertEqual(image.find_color(*rect,sample['color'],sample['sim'],sample['direction']),
                                     (sample['return_value'],sample['x'],sample['y']))
    def test_unverified_or_broken_inputs_raise_instead_of_low_hp(self):
        for spec in (None,'@FFFFFF','missing-key','FFFFFF-000000|nothex'):
            with self.assertRaises(color.ColorContractError):color.parse_color(spec,0.9)
        image=color.PixelImage(1,1,b'\x00\x00\x00')
        with self.assertRaises(color.ColorContractError):image.find_color(0,0,2,2,'000000',1)
        with self.assertRaises(color.ColorContractError):image.find_color(0,0,1,1,'000000',1,9)
    def test_sparse_axis_order_matches_native(self):
        # Diagonal hits distinguish row-first from column-first scan order.
        rgb=bytes((0,0,0,145,16,10,145,16,10,0,0,0))
        image=color.PixelImage(2,2,rgb)
        self.assertEqual(image.find_color(0,0,2,2,'91100A',1,0),(1,1,0))
        self.assertEqual(image.find_color(0,0,2,2,'91100A',1,5),(1,0,1))
        self.assertTrue(image.contains_color(0,0,2,2,'91100A',1))
    def test_picture_input_ordering_and_color_priority(self):
        d=json.loads((EVIDENCE/'picture-input-oracle-reset-outputs.json').read_text(encoding='utf-8-sig'))
        self.assertTrue(d['ok']);self.assertTrue(d['output_variants_reset'])
        n=0
        for sample in d['samples']:
            self.assertTrue(sample['input_validated'])
            rgb=bytearray([17,34,51]*64)
            dots={'cross':[(3,2),(2,3)],'red-first':[(3,2)],'white-first':[(3,2)],'right-boundary':[(4,2)],'bottom-boundary':[(2,4)]}[sample['layout']]
            for x,y in dots:rgb[(y*8+x)*3:(y*8+x)*3+3]=bytes((145,16,10))
            if sample['layout'].endswith('first'):rgb[(2*8+2)*3:(2*8+2)*3+3]=b'\xff\xff\xff'
            image=color.PixelImage(8,8,rgb)
            with self.subTest(layout=sample['layout'],direction=sample['direction']):
                self.assertEqual(image.find_color(*sample['rect'],sample['color'],sample['similarity'],sample['direction']),
                                 (sample['return_value'],sample['x'],sample['y']))
            n+=1
        self.assertEqual(n,45)
    def test_native_center_removal_order(self):
        d=json.loads((EVIDENCE/'picture-input-oracle-center.json').read_text(encoding='utf-8-sig'))
        self.assertTrue(d['ok']);self.assertEqual(d['phase'],'center')
        grouped={}
        for s in d['samples']:
            self.assertTrue(s['input_validated']);grouped.setdefault((s['width'],s['height']),[]).append(s)
        for (w,h),samples in grouped.items():
            expected=[(s['x'],s['y']) for s in samples if s['return_value']==1]
            self.assertEqual(list(color.scan_points(2,2,2+w,2+h,4)),expected)
            self.assertEqual((samples[-1]['return_value'],samples[-1]['x'],samples[-1]['y']),(0,-1,-1))
        self.assertEqual(len(d['samples']),97)
    def test_center_heap_generalizes_to_rectangles(self):
        for w in range(1,13):
            for h in range(1,13):
                cx=w//2;cy=h//2
                reference=sorted(((x,y) for y in range(h) for x in range(w)),key=lambda p:((p[0]-cx)**2+(p[1]-cy)**2,p[1],p[0]))
                self.assertEqual(list(color.scan_points(0,0,w,h,4)),reference)
if __name__=='__main__':unittest.main(verbosity=2)
