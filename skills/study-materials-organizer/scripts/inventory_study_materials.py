from __future__ import annotations

import argparse
import csv
import re
import time
from pathlib import Path


CATEGORY_RULES = [
    ("知识清单与方法归纳", ["知识清单", "知识必备", "题型必备", "思维导图", "方法归纳"]),
    ("复习讲义", ["讲义", "高频考点"]),
    ("专项训练", ["专项训练", "专题练", "解题思路训练", "提优秘籍", "典型题型归类训练"]),
    ("通关卷与检测卷", ["通关卷", "检测卷", "模拟卷", "综合训练卷", "收官卷", "阶段性检测", "摸底考", "卷"]),
]
ORIGINAL_MARKERS = ["原卷版", "原卷", "学生版", "考试版", "试题版", "练习版", "空白卷"]
ANSWER_MARKERS = ["解析版", "教师版", "答案", "详解", "全解全析", "参考答案", "解析板"]
AMBIGUOUS_RE = re.compile(r"^(第\s*\d+\s*[讲课时]|专题\s*[0-9一二三四五六七八九十百]+|微专题\s*\d+)")
DOC_EXTS = {".doc", ".docx", ".pdf", ".ppt", ".pptx", ".xls", ".xlsx", ".zip", ".rar", ".7z", ".png", ".jpg", ".jpeg", ".emf", ".wmf", ".emmx"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    return parser.parse_args()


def classify_category(path: Path) -> str:
    text = " ".join(path.parts)
    if path.suffix.lower() in {".ppt", ".pptx"}:
        return "课件"
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".emf", ".wmf", ".emmx"}:
        return "素材归档"
    if path.suffix.lower() in {".zip", ".rar", ".7z"}:
        return "压缩包"
    for category, markers in CATEGORY_RULES:
        if any(marker in text for marker in markers):
            return category
    return "其他待整理"


def classify_version(path: Path) -> str:
    name = path.name
    if any(marker in name for marker in ORIGINAL_MARKERS):
        return "原卷版"
    if any(marker in name for marker in ANSWER_MARKERS):
        return "解析版"
    return "通用版"


def suggested_prefix(path: Path) -> str:
    stem = path.stem
    if not AMBIGUOUS_RE.match(stem):
        return ""
    for parent in reversed(path.parents):
        if parent == Path(path.anchor):
            continue
        name = parent.name
        if any(token in name for token in ("章", "数列", "圆锥曲线", "解析几何", "知识清单", "知识必备", "题型必备", "专题", "模块")):
            return name
    return path.parent.name


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    rows = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("~$"):
            continue
        if path.suffix.lower() not in DOC_EXTS:
            continue
        rows.append(
            {
                "relative_path": str(path.relative_to(root)),
                "file_name": path.name,
                "extension": path.suffix.lower(),
                "category": classify_category(path),
                "version": classify_version(path),
                "suggested_prefix": suggested_prefix(path),
            }
        )

    out = root / f"_资料清单_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["relative_path", "file_name", "extension", "category", "version", "suggested_prefix"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(out)
    print(f"rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
