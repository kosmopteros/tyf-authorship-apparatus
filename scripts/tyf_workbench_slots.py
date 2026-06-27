#!/usr/bin/env python3
"""Small explicit slot helper for Workbench HTML extensions.

This is an interim architecture hardening step. The v0.6 Workbench still owns the
base HTML, but live Workbench additions now pass through named anchors with
validation instead of anonymous ad-hoc replacements spread across the module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

ASIDE_BEFORE_IMAGES = "      <section>\n        <strong>Images</strong>"
SCRIPT_BEFORE_RENDER = "    document.getElementById('refreshData').addEventListener('click', reload);\n    render();"


@dataclass(frozen=True)
class WorkbenchSlots:
    aside_before_images: str = ""
    script_before_render: str = ""
    label_replacements: tuple[tuple[str, str], ...] = ()


class WorkbenchSlotError(RuntimeError):
    pass


def apply_workbench_slots(html: str, slots: WorkbenchSlots) -> str:
    problems: List[str] = []
    for old, new in slots.label_replacements:
        html = html.replace(old, new)
    if slots.aside_before_images:
        if ASIDE_BEFORE_IMAGES not in html:
            problems.append("missing aside-before-images anchor")
        else:
            html = html.replace(ASIDE_BEFORE_IMAGES, slots.aside_before_images + ASIDE_BEFORE_IMAGES)
    if slots.script_before_render:
        if SCRIPT_BEFORE_RENDER not in html:
            problems.append("missing script-before-render anchor")
        else:
            html = html.replace(SCRIPT_BEFORE_RENDER, "    document.getElementById('refreshData').addEventListener('click', async () => { await reload(); await pollLiveStatus(); });\n" + slots.script_before_render + "\n    render();\n    connectLiveStatus();")
    if problems:
        raise WorkbenchSlotError("Workbench HTML slot failure: " + ", ".join(problems))
    return html
