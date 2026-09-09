# Codex Skills

This repository collects reusable Codex Skills for local workflows. Each skill is a self-contained folder with a required `SKILL.md` file and optional supporting resources such as scripts, references, or assets.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `codex-ppt` | Generates visually unified image-based PowerPoint decks from articles, reports, papers, notes, or outlines. |
| `hatch-pet` | Creates, repairs, validates, visually QA's, and packages Codex-compatible animated pets and spritesheets. |
| `jupyter-notebook` | Creates, scaffolds, or edits clean reproducible Jupyter notebooks for experiments, explorations, and tutorials. |
| `study-materials-organizer` | Organizes Windows folders containing Chinese teaching materials, tutoring notes, practice sets, papers, slide decks, and mixed assets. |
| `text-polisher` | Rewrites or tightens short user-provided text while preserving meaning, tone intent, and factual details. |

## Skill Directory Structure

A typical Codex Skill uses this shape:

```text
skill-name/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- scripts/
|-- references/
`-- assets/
```

Only `SKILL.md` is required. Add optional folders only when they serve the skill:

- `agents/openai.yaml`: UI metadata and invocation policy.
- `scripts/`: reusable deterministic helpers.
- `references/`: detailed instructions loaded only when relevant.
- `assets/`: templates, images, fonts, or other reusable output resources.

## SKILL.md Format

Every `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: text-polisher
description: Rewrite or tighten short user-provided text while preserving meaning, tone intent, and important factual details.
---
```

The `name` should match the folder name. The `description` is important because Codex uses it to decide when the skill should be considered.

The Markdown body should contain the operational guidance Codex needs after the skill is selected. Keep it focused: describe the workflow, real constraints, and when to read supporting files.

## Installation

Copy one or more skill folders into your local Codex skills directory:

```powershell
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { "$HOME\.codex" }
Copy-Item -Recurse -Force .\skills\text-polisher "$CodexHome\skills\text-polisher"
```

To install every skill in this repository:

```powershell
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { "$HOME\.codex" }
New-Item -ItemType Directory -Force "$CodexHome\skills" | Out-Null
Copy-Item -Recurse -Force .\skills\* "$CodexHome\skills\"
```

Restart Codex if a newly installed skill does not appear immediately.

## Validation

Validate an installed skill with the bundled validator when available:

```powershell
python "$env:CODEX_HOME\skills\.system\skill-creator\scripts\quick_validate.py" "$env:CODEX_HOME\skills\text-polisher"
```

A valid skill should have:

- A folder name that matches the frontmatter `name`.
- A concise, discriminating `description`.
- No unfinished scaffold placeholders.
- Supporting files that are referenced from `SKILL.md` when they should be loaded.

## Usage

Invoke a skill explicitly:

```text
$text-polisher Please make this message more concise: I wanted to check whether we can finish this today because the next step depends on it.
```

Codex can also use a skill implicitly when a request matches the skill description.

## Maintenance Notes

- Keep skill instructions narrow and practical.
- Prefer references for long conditional details instead of bloating `SKILL.md`.
- Add scripts when deterministic execution is more reliable than repeatedly generating code.
- Validate after every meaningful change.
