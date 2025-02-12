from __future__ import annotations

from typing import Dict

dm = 1e-1
dm2 = 1e-2
L = 1e-3
kg_dm3 = 1e3
dm3_kg = 1e-3
kgfdm_kg = 0.98
kgf_dm2 = 980
dm_s = 0.1


def format_compo_string(compo_dict: Dict[str, float]) -> str:
    return "\n".join(f"{percentage:>3.1%} {ingredient}" for ingredient, percentage in compo_dict.items()) + "\n"
