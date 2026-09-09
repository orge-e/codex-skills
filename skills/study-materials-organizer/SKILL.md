---
name: study-materials-organizer
description: Organize Windows folders that contain Chinese teaching materials, tutoring notes, practice sets, exam papers, slide decks, and mixed document assets. Use when Codex needs to classify files into lecture, practice, knowledge-list, paper, slides, archive, or asset groups; split original-paper files from answer files; add source prefixes to ambiguous names like Di1jiang or Zhuanti01; deduplicate by content hash before moving; or batch-convert Word documents to PDF with Microsoft Word COM to avoid MathType or formula garbling.
---

# Study Materials Organizer

Use this skill for recurring cleanup of large education-material folders on Windows.

## Workflow

1. Inventory the target tree with `scripts/inventory_study_materials.py`.
2. Review the inferred category, version, and rename prefix in the CSV.
3. Organize with `scripts/organize_study_materials.py` in `--dry-run` first, then rerun with `--apply`.
4. Convert Word files to PDF with `scripts/batch_word_to_pdf.py` when PDF output is required.
5. Verify counts and review the generated logs before claiming completion.

## Use Inventory First

Run:

```powershell
python scripts\inventory_study_materials.py --root "E:\path\to\folder"
```

Use the CSV to answer:

- what document types exist
- how files are classified
- which files look like original-paper or answer-side versions
- which names need a source prefix

## Organize Safely

Run a dry run first:

```powershell
python scripts\organize_study_materials.py `
  --root "E:\path\to\folder" `
  --dry-run
```

Then apply:

```powershell
python scripts\organize_study_materials.py `
  --root "E:\path\to\folder" `
  --apply
```

Default behavior:

- move files, do not copy
- create a small set of top-level folders
- classify by content markers from `references/classification-rules.md`
- separate `original`, `answer`, and `generic` versions
- add a source prefix when the basename starts with ambiguous numbering
- deduplicate by SHA-256 hash before moving
- if the destination name already exists with different content, keep both and prefix the incoming file with `buchongban-`
- skip Word temp files and generated log folders

## Convert Word To PDF Without Formula Garbling

Always use Microsoft Word COM for these teaching-material folders when formulas or MathType objects may exist.

Typical command:

```powershell
python scripts\batch_word_to_pdf.py `
  --root "E:\path\to\folder" `
  --pdf-dir-name PDF `
  --skip-markers "jiexiban,jiaoshiban,daan,xiangjie,quanjiequanxi,cankaodaan"
```

Convert everything and delete Word after successful export:

```powershell
python scripts\batch_word_to_pdf.py `
  --root "E:\path\to\folder" `
  --convert-all `
  --delete-source `
  --pdf-dir-name PDF `
  --move-existing-pdfs
```

Behavior:

- preserve relative paths under the target `PDF` folder
- restart Word periodically to reduce COM hangs
- overwrite existing same-name PDFs
- delete source `.doc` or `.docx` only after a successful export when `--delete-source` is set
- write timestamped logs with success and failure rows

## Review Rules

- prefer hash-based duplicate detection over filename-only checks
- keep paths shallow
- merge into an existing useful top-level structure instead of creating a parallel tree
- when ambiguous numbered files land in the same directory, prefix with the nearest useful source folder or chapter label
- treat student, original-paper, exam, test, and practice markers as original-paper side unless the user overrides
- treat teacher, answer, explanation, and solution markers as answer side unless the user overrides

## Resources

- Classification rules: `references/classification-rules.md`
- Inventory script: `scripts/inventory_study_materials.py`
- Organizer script: `scripts/organize_study_materials.py`
- Word-to-PDF script: `scripts/batch_word_to_pdf.py`
