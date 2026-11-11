import unittest

from compare_skill_island_retained import compare_host, compare_module
from export_skill_island_retained import build
from replay_shared_battle import load


class SkillIslandRetainedTests(unittest.TestCase):
    def test_every_original_record_and_controlled_path(self):
        plans = {}
        for module,expected in (('09',(934,104,30,4647)),('10',(1315,329,41,5621))):
            raw = load(f'programs/{module}.json')
            plan = load(f'data/skill-island-retained-{module}.json')
            plans[module] = plan
            self.assertEqual(plan['actions'],build(module,raw)['actions'])
            for a in plan['actions']:
                self.assertEqual([a[k] for k in ('opcode','location','operand','field_3')],raw['code'][a['record']])
                if a['source_sl'] is not None:
                    self.assertEqual(a['source'],raw['strings'][a['source_sl']])
            self.assertEqual(set(map(int,plan['boundaries'])),set(raw['missing_records']))
            report = compare_module(module,plan,load(f'data/battle-small-{module}-cases.json'),
                                    load(f'verification/original-battle-small-{module}.json'))
            self.assertEqual((len(plan['actions']),len(plan['boundaries']),report['cases'],report['external_events']),expected)
            self.assertEqual(report['cursor_positions'],[(314,256),(1820,950)] if module=='10' else [])
        host = compare_host(load('verification/original-skill-island-host.json'),
                            load('verification/original-callback-vm-test.json'),plans)
        self.assertEqual(host['default_boundaries'],{'09':12,'10':17})
        self.assertEqual((host['form_cases'],host['form_steps'],host['callback_cases']),(6,30,2))
