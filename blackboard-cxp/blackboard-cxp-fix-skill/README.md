# Blackboard CXP Fix Skill

Reusable agent skill for diagnosing and repairing Blackboard ULTRA CXP
course-package import failures. Bundles the **8-point defect recipe**, eight
pure-stdlib Python 3.8+ scripts, and reference notes.

No external dependencies. No personal information. No phone-home.

## What's inside

```
blackboard-cxp-fix-skill/
├── SKILL.md              ← invocation conditions + defect recipe + workflow
├── README.md             ← this file
├── LICENSE               ← MIT
├── scripts/              ← 8 pure-stdlib Python scripts (audit + fixes)
└── references/           ← markdown notes the agent can read
    ├── 8point_recipe.md
    ├── decision_tree.md
    └── do_not_do.md
```

## Install — Claude Code

```bash
# user-level (~/.claude/skills/ on macOS/Linux, %USERPROFILE%\.claude\skills\ on Windows)
mkdir -p ~/.claude/skills
unzip blackboard-cxp-fix-skill.zip -d ~/.claude/skills/
```

Or for a project-local skill:

```bash
mkdir -p .claude/skills
unzip blackboard-cxp-fix-skill.zip -d .claude/skills/
```

After install, restart Claude Code or reload skills. The agent will surface
the skill automatically when the user describes a Blackboard import problem.

## Install — Codex CLI

```bash
mkdir -p ~/.codex/skills
unzip blackboard-cxp-fix-skill.zip -d ~/.codex/skills/
```

The Codex CLI auto-discovers the skill on next launch.

## Install — manual / other agents

Any agent runtime that reads a `SKILL.md` with YAML frontmatter (`name`,
`description`) will work. Drop the directory wherever your agent looks for
skills. The frontmatter description controls when the skill is invoked.

## Standalone use (no agent)

Each script in `scripts/` is a standalone Python 3.8+ CLI. Example:

```bash
# Audit a freshly extracted package
python scripts/audit_8point.py /path/to/extracted/package

# Fix disabled LINKs
python scripts/fix_disabled_links.py /path/to/extracted/package

# Restore missing LINKs from the original archive
python scripts/restore_missing_links.py \
    --orig /path/to/original/archive \
    --cur  /path/to/working/package
```

See `SKILL.md` for the complete script index.

## Recommended workflow

1. Export the source course as an archive ZIP from the Blackboard UI.
2. **Backup** the ZIP under a separate path. Never modify it.
3. **Extract** to a working directory.
4. `python scripts/audit_8point.py <working-dir>` — surface a baseline.
5. Apply the indicated fix script, **one defect at a time**.
6. Re-run `audit_8point.py` — edits themselves can introduce new defects.
7. Repackage with `Compress-Archive` (PowerShell) or `zip -r` (POSIX).
8. **Sandbox import** + click every visible item. Inspect convert-time logs
   AND runtime behavior.
9. Production import only after the sandbox is clean.

## Hard rules

- One defect, one version (`v1`, `v2`, …) — never bundle.
- Never modify the original backup ZIP.
- Never overwrite a resource ID with a different `bb:type` payload.
- Never remove `ULTRA_ASSESSMENT_MARKER` to silence logs.
- Never delete `<item>` from a real multi-choice quiz.
- Never delete a disabled LINK — flip its flag instead.
- Always use `re.sub(r'<ISAVAILABLE\s+value="false"\s*/>', ...)` — never
  single-line literal replace.
- Always sandbox-test before production.

## License

MIT (see `LICENSE`).

Free to use, modify, and redistribute with attribution. Provided "as-is" —
the maintainer makes no warranty about behavior in any particular Blackboard
deployment. Validate every fix in a sandbox course first.
