"""Render the report as a single-file, self-contained interactive HTML dashboard.

The template lives in dashboard_template.py (plain string, no f-string
escaping); __DATA_JSON__ is injected here. Design: premium light SaaS style
("Solv."-inspired) with a full dark-mode toggle, animated bar charts, health
score ring, and staggered entrance animations. Zero external dependencies.
"""

from __future__ import annotations

import json
from typing import Any

from .dashboard_template import TEMPLATE


def render_dashboard(report: dict[str, Any]) -> str:
    data_json = json.dumps(report, default=str)
    return TEMPLATE.replace("__DATA_JSON__", data_json)
