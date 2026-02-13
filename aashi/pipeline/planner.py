from .types import Intent, Plan


class TaskPlanner:
    def plan(self, intent: Intent) -> Plan:
        return Plan(actions=[{"kind": intent.kind, "payload": intent.payload}])
