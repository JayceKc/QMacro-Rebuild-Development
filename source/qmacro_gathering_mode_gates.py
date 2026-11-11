"""Opt-in preview of inferred 08 mode gates and the preserved routines they call."""
from copy import deepcopy

from qmacro_gathering_main import GatheringMainMachine


class GatheringModeGateMachine(GatheringMainMachine):
    def __init__(self, plan, gate_plan, read_context, initial, entry=100):
        if (entry not in gate_plan["entries"] or gate_plan["module"] != 8
                or gate_plan["source_program_sha256"] != plan["source_program_sha256"]):
            raise ValueError("Unreviewed gathering gate entry or source")
        super().__init__(plan, read_context, initial, 593)
        actions = {action["record"]: deepcopy(action) for action in gate_plan["actions"]}
        if len(actions) != len(gate_plan["actions"]) or not actions.keys() <= self.missing:
            raise ValueError("Gathering gate must use only separate, originally missing positions")
        self.actions.update(actions)
        self.missing.difference_update(actions)
        self.pc = entry

    def step(self):
        action = self.actions.get(self.pc)
        if not self.done and action and action["kind"] == "if_zero_unresolved":
            at = self.pc
            if not self.flag:
                self.done = True
                self.reason = "unresolved_sdk_miss_edge"
            else:
                self.pc += 1
            return {"record": at, "kind": "if_zero", "taken": not self.flag,
                    "target": None if not self.flag else self.pc}
        return super().step()
