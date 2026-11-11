"""Link the remaining callable battle bodies, with checked entry/return pairs."""
import hashlib
import json

from export_battle_recovery import CANDIDATES
from export_battle_routes import build_routes
from export_cube_routines import PROJECT


TAIL_RANGES = {
    '01': ((1020,1323,'按鈕進本'),(1325,1589,'再來一次與入場確認'),(11700,11723,'技能圖擷取'),
           (11875,11959,'切換道具欄'),(12002,12388,'圖四'),(12390,12615,'播放計時處理')),
    '03': ((527,837,'按鈕進本'),(6013,6097,'切換道具欄'),(6099,6324,'播放計時處理'),
           (6326,6367,'檢查剩餘次數'),(6369,6419,'進本畫面確認')),
    '06': ((573,667,'覺醒'),(669,854,'死亡處理'),(856,1156,'按鈕進本'),
           (1158,1441,'再來一次與入場確認'),(8599,8619,'技能圖擷取'),(8754,8838,'切換道具欄'),
           (8840,9226,'圖四'),(10180,10251,'畫面點擊與等待')),
}
ENTRY_VERSION_CHECKPOINTS = {'01':1042,'03':550,'06':896}
ENTRY_VERSION = 'VFDDEA0D0CE9FB68B4D6A65757378756D'


def build_tail(module, raw, base, additional_ranges=()):
    plan = build_routes(module,raw,base,TAIL_RANGES[module]+tuple(additional_ranges))
    checkpoint = ENTRY_VERSION_CHECKPOINTS[module]
    op,_,operand,_ = raw['code'][checkpoint]
    if op!=27 or raw['strings'][operand]!=ENTRY_VERSION:
        raise ValueError(('Unexpected instance entry checkpoint',module,checkpoint))
    plan.setdefault('reviewed_checkpoints',[]).append(checkpoint)
    plan['name'] = '戰鬥、進本、地圖、換角色與技能擷取'
    return plan


def main():
    CANDIDATES.mkdir(exist_ok=True)
    for module,ranges in TAIL_RANGES.items():
        program = (PROJECT/f'programs/{module}.json').read_bytes()
        base = (PROJECT/f'data/battle-{module}.json').read_bytes()
        plan = build_tail(module,json.loads(program),json.loads(base))
        plan.update(source_program_sha256=hashlib.sha256(program).hexdigest(),
                    base_plan_sha256=hashlib.sha256(base).hexdigest())
        (CANDIDATES/f'battle-tail-{module}.json').write_text(
            json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(module,sum(last-first+1 for first,last,_ in ranges),len(plan['actions']))


if __name__=='__main__':
    main()
