from __future__ import annotations

import argparse
import csv
import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

import pythoncom
import win32com.client


WORD_EXTS = {".doc", ".docx"}


@dataclass
class ResultRow:
    source: str
    target: str
    status: str
    detail: str


class WordExporter:
    def __init__(self, restart_every: int = 20) -> None:
        self.restart_every = restart_every
        self.word = None
        self.count = 0

    def start(self) -> None:
        pythoncom.CoInitialize()
        self.word = win32com.client.DispatchEx("Word.Application")
        self.word.Visible = False
        self.word.DisplayAlerts = 0

    def stop(self) -> None:
        if self.word is not None:
            try:
                self.word.Quit()
            except Exception:
                pass
            self.word = None
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass

    def maybe_restart(self) -> None:
        if self.word is None:
            self.start()
            return
        if self.count and self.count % self.restart_every == 0:
            self.stop()
            self.start()

    def export(self, source: Path, target: Path) -> None:
        self.maybe_restart()
        doc = None
        try:
            doc = self.word.Documents.Open(str(source), False, True)
            doc.ExportAsFixedFormat(str(target), 17)
            self.count += 1
        finally:
            if doc is not None:
                try:
                    doc.Close(False)
                except Exception:
                    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--pdf-dir-name", default="PDF")
    parser.add_argument("--skip-markers", default="")
    parser.add_argument("--convert-all", action="store_true")
    parser.add_argument("--delete-source", action="store_true")
    parser.add_argument("--move-existing-pdfs", action="store_true")
    parser.add_argument("--restart-every", type=int, default=20)
    parser.add_argument("--log-prefix", default="_PDF转换记录")
    return parser.parse_args()


def should_convert(path: Path, convert_all: bool, skip_markers: list[str], pdf_root: Path) -> bool:
    if not path.is_file():
        return False
    if pdf_root in path.parents:
        return False
    if path.name.startswith("~$"):
        return False
    if path.suffix.lower() not in WORD_EXTS:
        return False
    if convert_all:
        return True
    return not any(marker and marker in path.name for marker in skip_markers)


def build_target(root: Path, pdf_root: Path, source: Path) -> Path:
    relative = source.relative_to(root)
    return (pdf_root / relative).with_suffix(".pdf")


def move_existing_pdfs(root: Path, pdf_root: Path) -> list[tuple[str, str]]:
    moved: list[tuple[str, str]] = []
    for path in root.rglob("*.pdf"):
        if pdf_root in path.parents:
            continue
        target = pdf_root / path.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.unlink()
        shutil.move(str(path), str(target))
        moved.append((str(path), str(target)))
    return moved


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    pdf_root = root / args.pdf_dir_name
    skip_markers = [part.strip() for part in args.skip_markers.split(",")]
    log_dir = root.parent / f"{args.log_prefix}_{time.strftime('%Y%m%d_%H%M%S')}"
    log_dir.mkdir(parents=True, exist_ok=True)

    docs = sorted(
        [path for path in root.rglob("*") if should_convert(path, args.convert_all, skip_markers, pdf_root)],
        key=lambda p: str(p).lower(),
    )

    results: list[ResultRow] = []
    exporter = WordExporter(restart_every=args.restart_every)

    try:
        exporter.start()
        for idx, source in enumerate(docs, start=1):
            target = build_target(root, pdf_root, source)
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    target.unlink()
                exporter.export(source, target)
                if not target.exists():
                    raise RuntimeError("PDF not generated")
                if args.delete_source:
                    source.unlink()
                results.append(ResultRow(str(source), str(target), "ok", ""))
            except Exception as exc:
                results.append(ResultRow(str(source), str(target), "error", str(exc)))
            if idx % 20 == 0:
                print(f"processed {idx}/{len(docs)}")
    finally:
        exporter.stop()

    moved_pdfs = move_existing_pdfs(root, pdf_root) if args.move_existing_pdfs else []

    with (log_dir / "convert_log.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "status", "detail"])
        writer.writeheader()
        for row in results:
            writer.writerow(row.__dict__)

    with (log_dir / "moved_existing_pdfs.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target"])
        writer.writeheader()
        for source, target in moved_pdfs:
            writer.writerow({"source": source, "target": target})

    summary = {
        "root": str(root),
        "pdf_root": str(pdf_root),
        "source_count": len(docs),
        "ok_count": sum(1 for row in results if row.status == "ok"),
        "error_count": sum(1 for row in results if row.status == "error"),
        "delete_source": args.delete_source,
        "move_existing_pdfs": args.move_existing_pdfs,
        "moved_existing_pdf_count": len(moved_pdfs),
        "log_dir": str(log_dir),
    }
    (log_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["error_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
