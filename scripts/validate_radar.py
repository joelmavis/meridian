#!/usr/bin/env python3
"""验证 Meridian 每日或每周雷达的基本结构。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TRACKS = {
    "欧洲科技政治",
    "AI治理与AI主权",
    "中美欧科技关系",
    "全球AI地缘政治与多边治理",
    "企业AI治理",
}
ACTIONS = {"忽略", "保存", "快速研究", "专题研究", "内容选题"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("radar", type=Path)
    parser.add_argument("--weekly", action="store_true")
    args = parser.parse_args()
    text = args.radar.read_text(encoding="utf-8")
    errors: list[str] = []
    headings = re.findall(r"^### (\d+)\. ", text, re.MULTILINE)
    if not args.weekly and len(headings) != 3:
        errors.append("daily radar must have exactly three core signals")
    for block in re.split(r"^### \d+\. ", text, flags=re.MULTILINE)[1:]:
        for label in (
            "优先级：",
            "发生了什么：",
            "为什么重要：",
            "所属研究方向：",
            "与欧洲 AI 治理的关系：",
            "来源：",
            "建议动作：",
        ):
            if label not in block:
                errors.append(f"signal missing {label}")
        priority = re.search(r"优先级：[ \t]*(P[123])", block)
        if not priority:
            errors.append("signal has invalid priority")
        track = re.search(r"所属研究方向：[ \t]*([^\n]+)", block)
        if track and track.group(1).strip() not in TRACKS:
            errors.append("signal has invalid research track")
        action = re.search(r"建议动作：[ \t]*([^\n]+)", block)
        if action and action.group(1).strip() not in ACTIONS:
            errors.append("signal has invalid action")
    if errors:
        print("INVALID")
        print("\n".join(sorted(set(errors))))
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
