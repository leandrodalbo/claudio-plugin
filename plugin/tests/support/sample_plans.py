def build_valid_plan():
    """A new plan: cycle 1 done; cycles 2, 2b and 3 not done."""
    return {
        "title": "Phase machine",
        "status": "active",
        "goal": "Know the current phase.",
        "cycles": [
            {
                "key": "1",
                "what": "Read the phase",
                "done": True,
                "notes": [],
                "files": ["tdcg/state/phase_file.py"],
            },
            {
                "key": "2",
                "what": "next",
                "done": False,
                "notes": ["COMMIT wraps to SPECIFY"],
                "files": ["tdcg/state/*.py", "tests/state/test_phase_file.py"],
            },
            {
                "key": "2b",
                "what": "next creates the folder",
                "done": False,
                "notes": [],
                "files": ["tdcg/state/phase_file.py"],
            },
            {"key": "3", "what": "back", "done": False, "notes": [], "files": ["tdcg/**"]},
        ],
    }


def build_plan_with_all_cycles_done():
    plan = build_valid_plan()
    for cycle in plan["cycles"]:
        cycle["done"] = True
    return plan


def build_plan_with_one_cycle_left():
    """Only cycle 3 is not done."""
    plan = build_valid_plan()
    for cycle in plan["cycles"][:-1]:
        cycle["done"] = True
    return plan


def build_plan_with_field_set_to(field, value):
    plan = build_valid_plan()
    plan[field] = value
    return plan


def build_plan_with_schema_link():
    return build_plan_with_field_set_to("$schema", "./plan.schema.json")


def build_plan_without_field(field):
    plan = build_valid_plan()
    del plan[field]
    return plan


def build_plan_with_cycle_field_set_to(key, field, value):
    plan = build_valid_plan()
    _find_cycle_by_key(plan, key)[field] = value
    return plan


def build_plan_without_cycle_field(key, field):
    plan = build_valid_plan()
    del _find_cycle_by_key(plan, key)[field]
    return plan


def _find_cycle_by_key(plan, key):
    return next(cycle for cycle in plan["cycles"] if cycle["key"] == key)
