#!/usr/bin/env python3
"""验证 Meridian HTML 日报的基本结构。"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REQUIRED_LABELS = (
    "重要性：",
    "优先级：",
    "发生了什么：",
    "为什么值得关注：",
    "适合做什么类型内容：",
    "来源：",
)
CONTENT_TYPES = {
    "深度研究",
    "快评文章",
    "短视频",
    "X 讨论帖",
    "播客选题",
    "仅纳入观察清单",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("radar", type=Path)
    args = parser.parse_args()
    text = args.radar.read_text(encoding="utf-8")
    errors: list[str] = []
    if "<html" not in text.lower() or "</html>" not in text.lower():
        errors.append("daily radar must be a complete HTML document")
    if "<h1>Meridian｜全球 AI 治理晨报</h1>" not in text:
        errors.append("daily radar has an invalid title")
    if "今日 10 条消息" not in text:
        errors.append("daily radar missing the ten-message section")
    articles = re.findall(r"<article\b[^>]*>(.*?)</article>", text, re.DOTALL | re.IGNORECASE)
    if len(articles) != 10:
        errors.append("daily radar must have exactly ten messages")
    for article in articles:
        for label in REQUIRED_LABELS:
            if label not in article:
                errors.append(f"message missing {label}")
        if not re.search(r"优先级：\s*</?[^>]*>?\s*P[123]|优先级：\s*P[123]", article):
            errors.append("message has invalid priority")
        if not re.search(r"重要性：\s*</?[^>]*>?\s*(高|中|低)|重要性：\s*(高|中|低)", article):
            errors.append("message has invalid importance")
        if not any(content_type in article for content_type in CONTENT_TYPES):
            errors.append("message has invalid content type")
        if not re.search(r"<a\s+href=[\"'][^\"']+[\"']", article, re.IGNORECASE):
            errors.append("message missing a source link")
    for heading in ("本日判断", "可确认事实", "基于现有事实的推论", "今日建议", "来源与方法说明"):
        if heading not in text:
            errors.append(f"daily radar missing {heading}")
    if errors:
        print("INVALID")
        print("\n".join(sorted(set(errors))))
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
