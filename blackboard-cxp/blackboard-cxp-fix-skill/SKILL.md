---
name: blackboard-cxp-fix
description: Diagnose and fix Blackboard ULTRA CXP course-package import failures and silent runtime errors. Invoke when the user mentions a Blackboard archive ZIP (`ArchiveExFile_*.zip`), a "content item failed to convert" error, an `MjYwNTA0L*` access-code log, an assignment that imports cleanly but does not open on click, or a need to bulk-update due dates across an exported package. Implements the 8-point defect recipe.
---

# Blackboard CXP Modify-and-Re-Import Fix Skill

This skill detects and repairs the eight defect classes that surface when a
Blackboard ULTRA CXP archive (`ArchiveExFile_*.zip`) is exported, edited, and
re-imported. It is language-agnostic, single-purpose, and operates only on a
local extracted package directory — it does **not** talk to the Blackboard
server.

## When to use

Invoke this skill when:

- Import fails with **"<item> failed to convert"** or **"Blogs aren't supported"**.
- Import succeeds but a clicked assignment / discussion does **nothing** (silent
  runtime failure).
- Each click appends a base64 access-code reference like `MjYwNTA0L*`.
- You need to **bulk-update due dates** across a Gradebook resource.
- You need to **embed images** (csfiles + sidecar + manifest) into a content page.
- You need to **replace** a content-page body without disturbing dates / flags
  / handler.

Do **NOT** use this skill for: LDAP integration, gradebook calculation columns,
external-tool OAuth, Building-Block / LTI registration. Those require admin
intervention and live outside the package.

## The 8-point defect recipe

| # | Class | Phase | Script |
|---|---|---|---|
| 1 | Orphan manifest declarations | convert-time | `audit_8point.py` (diagnostic only) |
| 2 | Retired-tool handlers (Journal / Blog / Wiki) | convert-time | `fix_journal_blog_dependency.py` |
| 3 | Wrong-type substitution | convert-time | manual restore from original archive |
| 4 | Empty leaf content | convert-time | manual content addition |
| 5 | Disabled LINK resources | runtime | `fix_disabled_links.py` |
| 6 | Missing LINK resources | runtime | `restore_missing_links.py` |
| 7 | ULTRA marker × classic-QTI conflict | runtime | `fix_ultra_qti_conflict.py` |
| 8 | Whitespace-tolerant ISAVAILABLE replace | tooling | (use multi-line regex; see code) |

Convert-time defects raise an explicit error at import. Runtime defects pass
import cleanly but break on the first student click — these are the dangerous
ones.

## Standard workflow

1. **Export** the source course as an archive ZIP from Blackboard UI.
2. **Backup** the original ZIP separately and never modify it.
3. **Extract** to a working directory.
4. **Audit** — run `python scripts/audit_8point.py /path/to/extracted` first
   to surface a baseline.
5. **Modify** — apply fix scripts one defect at a time. Save each pass as a new
   version (`v1`, `v2`, …).
6. **Re-audit** — edits themselves can introduce new defects.
7. **Repackage** — `Compress-Archive` (Windows) or `zip -r` (Linux/macOS).
8. **Sandbox import** — actually click every visible item.
9. **Production import** — only after the sandbox is clean.

## Hard rules — do NOT do these

1. Modify the original backup ZIP.
2. Overwrite an existing resource ID with a different `bb:type` payload — issue
   a new ID instead.
3. Remove `ULTRA_ASSESSMENT_MARKER` to silence access-code logs (the marker is
   the trigger for ULTRA rendering — items will stop opening).
4. Remove `<item>` from a real multi-choice quiz (the defect-7 fix is for
   ULTRA assignment surfaces only, not real quizzes).
5. Delete a disabled LINK to "clean it up" — that creates defect 6.
6. Use a single-line `c.replace('<ISAVAILABLE value="false"/>', ...)` literal —
   it silently misses multi-line FLAGS XML; always use
   `re.sub(r'<ISAVAILABLE\s+value="false"\s*/>', ...)`.
7. Hand-build a new `<FORUM>` resource — reuse the existing course-wide
   discussion board with a subject-prefix convention.
8. Bundle every fix into one ZIP — one defect, one version (rollback + paper
   trail).
9. Recompute `.bb-package-sig` — Blackboard import does not validate it and
   you cannot recompute it without Blackboard's private key.

## Operational defaults

- Place new media at xid range `≥ 990000` to avoid collisions with the
  existing `8-digit` xids.
- DUE dates use the `YYYY-MM-DD HH:MM:SS CDT|CST` format. Summer term in the
  US is CDT (UTC-5); validate the timezone string but Blackboard's parser
  tolerates either.
- For multi-line FLAGS XML, regex matching is mandatory — single-line literal
  replace silently misses partial cases.
- After every fix, re-run `audit_8point.py` to verify no new defects were
  introduced.

## Script index

All scripts in `scripts/` are pure Python 3.8+ stdlib — no dependencies.

- **`audit_8point.py`** — diagnostic; runs all 8 checks, prints PASS/FAIL,
  exits 0/1.
- **`fix_disabled_links.py`** — flips `ISAVAILABLE="false"` to `"true"` on
  LINK resources using a multi-line-tolerant regex. Defect 5.
- **`restore_missing_links.py`** — restores LINK files + manifest declarations
  from the original archive. Defect 6.
- **`fix_journal_blog_dependency.py`** — strips Journal / Blog / Wiki tool
  data + LINK + manifest declarations + flips the visible CONTENT's handler
  to `resource/x-bb-document`. Defect 2.
- **`fix_ultra_qti_conflict.py`** — empties the QTI `<section>` body for
  asmt-test-link items carrying `ULTRA_ASSESSMENT_MARKER`, while preserving
  the marker. Auto-skips real quizzes (any item containing
  `<response_lid>`). Defect 7.
- **`update_due_dates.py`** — bulk updates `<DUE>` fields inside
  `<OUTCOMEDEFINITION>` blocks from a JSON schedule. Warns on Sundays /
  holidays.
- **`embed_image.py`** — adds an image as `csfiles/home_dir/__xid-N_1.<ext>`
  + sidecar XML + `<resource>` declaration; prints the
  `@X@EmbeddedFile.requestUrlStub@X@` snippet for the body HTML.
- **`replace_body.py`** — replaces only the body HTML inside
  `<CONTENT><BODY><TEXT>...</TEXT></BODY></CONTENT>`; preserves dates /
  flags / handler / parent.

## Reasoning sketch for the agent

When the user describes a Blackboard import problem, classify it:

- "**fails to convert**" → defects 1, 2, 3, or 4 (convert-time)
  - "Blogs aren't supported" / "Journal" / "Wiki" → defect 2
  - "missing referenced file" → defect 1
- "**imports OK but click does nothing**" → defects 5 or 6 (runtime LINK chain)
  - Disabled LINK exists in package → defect 5
  - LINK file missing entirely → defect 6 (need original archive to restore)
- "**access-code log `MjYwNTA0L*`**" → defect 7 (ULTRA × QTI conflict)
- "**fix script worked on some but not all**" → defect 8 (multi-line FLAGS)

Then run `audit_8point.py` first, apply the indicated fix script, re-audit,
repackage, and instruct the user to sandbox-test before production import.

Always preserve the original archive untouched — every fix is a new version.

## License

Free to use with attribution. Provided "as-is" — no warranty for production
environments. Always sandbox-test first.
