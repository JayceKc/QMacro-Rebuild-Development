"""Add the preserved map and character selection routines without top-level skips."""
import hashlib
import json

from export_battle_control import build
from export_battle_recovery import CANDIDATES, RECOVERY_RANGES
from export_battle_restart import RESTART_RANGES
from export_cube_routines import PROJECT


ROUTE_RANGES = {
    '01': ((4059,4847,'圖二'),(4849,5118,'判斷紫金門'),(5120,6781,'圖三'),
           (8663,8793,'完成後操作'),(8795,10953,'換角色'),
           (10955,11167,'角色選擇錯誤檢查'),(11169,11282,'返回角色畫面'),
           (11284,11340,'換角前置'),(11342,11584,'辨識並進入角色'),
           (11961,12000,'三次周獎勵')),
    '03': ((3084,3258,'完成後操作'),(3260,5410,'換角色'),(5412,5883,'角色選擇錯誤檢查')),
    '06': ((3864,4652,'圖二'),(4654,4955,'判斷紫金門'),(4957,6618,'圖三')),
}
MAP_SCAN_CHECKPOINTS = {'01': (4080,4835), '06': (3885,4640)}


def build_routes(module, raw, base, additional_ranges=()):
    ranges = ROUTE_RANGES[module]+tuple(additional_ranges)
    for start,end,_ in ranges:
        op,_,jump,_ = raw['code'][start-1]
        if op!=16 or start-1+jump!=end+1 or raw['code'][end][0]!=13:
            raise ValueError(('Unexpected skip or return',module,start,end))
    added = RECOVERY_RANGES[module]+RESTART_RANGES[module]+ranges
    plan = build(module,raw,base,added)
    if plan['boundaries']:
        raise ValueError(('Unexpected route boundary',module,plan['boundaries']))
    if module in MAP_SCAN_CHECKPOINTS:
        entry, target = MAP_SCAN_CHECKPOINTS[module]
        if raw['code'][entry-1][0]!=5 or raw['code'][entry-1][2]!=target:
            raise ValueError(('Unreviewed map scan bypass',module,entry,target))
        plan['reviewed_checkpoints'] = [entry]
    plan['name'] = '戰鬥、地圖流程與換角色'
    plan['scope'] = 'Linked preserved subroutines with explicit screen observations.'
    return plan


def main():
    CANDIDATES.mkdir(exist_ok=True)
    for module,ranges in ROUTE_RANGES.items():
        program = (PROJECT/f'programs/{module}.json').read_bytes()
        base = (PROJECT/f'data/battle-{module}.json').read_bytes()
        plan = build_routes(module,json.loads(program),json.loads(base))
        plan.update(source_program_sha256=hashlib.sha256(program).hexdigest(),
                    base_plan_sha256=hashlib.sha256(base).hexdigest())
        (CANDIDATES/f'battle-routes-{module}.json').write_text(
            json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(module,sum(last-first+1 for first,last,_ in ranges),len(plan['actions']))


if __name__=='__main__':
    main()
