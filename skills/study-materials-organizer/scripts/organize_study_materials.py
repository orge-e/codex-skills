from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import shutil
import time
from dataclasses import dataclass
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
SKIP_DIR_MARKERS = ("_整理记录_", "_PDF转换记录_", "_定向PDF转换记录_", "_资料清单_")


@dataclass
class ActionRow:
    source: str
    target: str
    action: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_category(path: Path) -> str:
    text = " ".join(path.parts)
    suffix = path.suffix.lower()
    if suffix in {".ppt", ".pptx"}:
        return "课件"
    if suffix in {".png", ".jpg", ".jpeg", ".emf", ".wmf", ".emmx"}:
        return "素材归档"
    if suffix in {".zip", ".rar", ".7z"}:
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
    if not AMBIGUOUS_RE.match(path.stem):
        return ""
    for parent in reversed(path.parents):
        if parent == Path(path.anchor):
            continue
        name = parent.name
        if any(token in name for token in ("章", "数列", "圆锥曲线", "解析几何", "知识清单", "知识必备", "题型必备", "专题", "模块")):
            return name
    return path.parent.name


def normalized_name(path: Path) -> str:
    prefix = suggested_prefix(path)
    if not prefix:
        return path.name
    stem = f"{prefix}-{path.stem}"
    return f"{stem}{path.suffix}"


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("~$"):
            continue
        if any(marker in path.parts for marker in SKIP_DIR_MARKERS):
            continue
        files.append(path)
    return files


def target_for(root: Path, path: Path) -> Path:
    category = classify_category(path)
    if category in {"课件", "素材归档", "压缩包"}:
        base = root / category
    else:
        version = classify_version(path)
        base = root / f"{category}-{version}"
    return base / normalized_name(path)


def same_file(a: Path, b: Path) -> bool:
    try:
        return os.path.samefile(a, b)
    except Exception:
        return a.resolve() == b.resolve()


def resolve_conflict(target: Path, source: Path) -> tuple[Path, str]:
    if not target.exists():
        return target, ""
    if sha256(target) == sha256(source):
        return target, "duplicate_same_hash"
    alt = target.with_name(f"补充版-{target.name}")
    return alt, "content_conflict_keep_both"


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    log_dir = root / f"_整理记录_{time.strftime('%Y%m%d_%H%M%S')}"
    log_dir.mkdir(parents=True, exist_ok=True)

    actions: list[ActionRow] = []
    seen_hashes: dict[str, Path] = {}

    for source in sorted(iter_files(root), key=lambda p: str(p).lower()):
        if log_dir in source.parents:
            continue
        target = target_for(root, source)
        if same_file(source, target):
            continue
        try:
            source_hash = sha256(source)
        except Exception as exc:
            actions.append(ActionRow(str(source), str(target), "error", str(exc)))
            continue

        existing_same_hash = seen_hashes.get(source_hash)
        if existing_same_hash is not None and existing_same_hash != source:
            actions.append(ActionRow(str(source), str(existing_same_hash), "skip_duplicate_hash", "seen_in_run"))
            if args.apply:
                source.unlink()
            continue

        final_target, detail = resolve_conflict(target, source)
        if detail == "duplicate_same_hash":
            actions.append(ActionRow(str(source), str(target), "skip_duplicate_hash", "existing_target"))
            if args.apply:
                source.unlink()
            continue

        actions.append(ActionRow(str(source), str(final_target), "move", detail))
        seen_hashes[source_hash] = final_target

        if args.apply:
            final_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(final_target))

    with (log_dir / "move_log.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "action", "detail"])
        writer.writeheader()
        for row in actions:
            writer.writerow(row.__dict__)

    print(log_dir)
    print(f"actions={len(actions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
