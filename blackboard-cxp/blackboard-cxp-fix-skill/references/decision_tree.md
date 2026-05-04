# Decision tree — which defect am I looking at?

Use this when you have a fresh import problem and don't yet know which
defect class is in play.

```
                     Sandbox import outcome?
                            │
       ┌────────────────────┼─────────────────────────┐
       │                    │                         │
A. Convert error    B. Imports OK,            C. Opens fine but
   message          click does nothing           access-code log
       │                    │                         │
       ▼                    ▼                         ▼
 Inspect error           Verify the              Suspect D7
 type                    LINK chain              ULTRA × QTI
       │                    │                         │
   ┌───┴───┐            ┌───┴───────┐         Empty the QTI
   │       │            │           │         <section>
   ▼       ▼            ▼           ▼         (assignment only;
 Blogs/  Missing     Disabled     Stripped    real quizzes →
 Wiki/   .dat        LINK         entirely    skip; never
 Journal file        present      (manifest   remove the
   │       │         in           AND .dat    marker)
   ▼       ▼         package      gone)
  D2      D1            │           │
                        ▼           ▼
                   Flip ISAVAILABLE  Restore from
                   → "true"          original archive
                   (D5)              + add manifest
                                     declaration (D6)
```

## A. Convert error message

The Blackboard import surfaces an explicit error.

| Message fragment | Likely class | Fix script |
|---|---|---|
| "Blogs aren't supported" / "Reflective Journal" | D2 | `fix_journal_blog_dependency.py` |
| "missing referenced file" / "resource not found" | D1 | restore from original / strip declaration |
| "Empty assessments converted to Question Banks" | D7 (latent) — see C below | `fix_ultra_qti_conflict.py` |
| Type mismatch / unexpected root element | D3 | manual restore |
| "<item> failed to convert" with empty body | D4 | manual content add |

## B. Imports OK, click does nothing

Silent runtime failure. The item appears in the course, the gradebook
column gets created, but nothing happens when a student clicks. This is the
**dangerous** category — there is no error message anywhere.

Run the visible-click-target ↔ LINK match check in `audit_8point.py`. Two
sub-cases:

1. **LINK file is in the package, but ISAVAILABLE="false"** → defect 5.
   Run `fix_disabled_links.py`.
2. **LINK file is missing entirely** (manifest declaration also gone) →
   defect 6. Run `restore_missing_links.py` against the original archive.

## C. Opens fine but appends an access-code log

The item opens correctly, but every render appends a base64-encoded log
reference like `MjYwNTA0L*` (decoded: `260504/_666818_1/2.log`). This is
**not the actual error message** — it's a server-log path. The contents
live in the file at that path; ask Blackboard admin if you need them.

This pattern signals **defect 7 — ULTRA marker × classic-QTI conflict**.

Diagnostic:

1. Confirm the visible CONTENT has
   `<EXTENDEDDATA><ENTRY key="ULTRA_ASSESSMENT_MARKER">true</ENTRY></EXTENDEDDATA>`.
2. Walk the LINK chain to the questestinterop file at the end.
3. Check if its `<section>` contains `<item>` elements that are NOT real
   multi-choice questions (no `<response_lid>`).

If yes → run `fix_ultra_qti_conflict.py`. The script auto-skips real
quizzes.

**Never remove the ULTRA marker itself.** That stops the item from opening
in ULTRA. The marker is the trigger for ULTRA rendering.

## After every fix

Re-run `audit_8point.py`. The fix itself can introduce new defects
(especially defect 8 — whitespace-tolerance bugs). Do not repackage until
the audit passes.
