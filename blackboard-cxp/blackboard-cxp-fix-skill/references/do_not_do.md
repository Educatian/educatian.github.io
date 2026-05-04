# Hard rules — never do these

These are the failure modes observed during the original 11+ iteration fix
marathon that produced this skill. Each one is here because someone (often
a prior coding agent) actually did it and broke a package.

## 1. Modify the original backup ZIP

The path under `03_Original-ZIPs-Backup/ArchiveExFile_*.zip` is the ground
truth and the rollback material. Every fix happens on a working copy. If
you lose the original, you lose the ability to restore missing LINKs
(defect 6) or wrong-type substitutions (defect 3).

## 2. Overwrite an existing resource ID with a different-type payload

Reasoning like *"this slot is empty, let's put a new assessment here"*
breaks the manifest's `bb:type` invariant — the manifest still says
`course/x-bb-coursemessagefolder` while the new payload's root is
`<questestinterop>`. This is defect 3.

If you need new content, **issue a fresh resource ID** and add a new
`<resource>` declaration.

## 3. Remove `ULTRA_ASSESSMENT_MARKER` to silence the access-code log

The marker is the trigger for ULTRA rendering. Remove it and the item
stops opening in ULTRA at all. The right answer is to empty the QTI body's
`<section>`, not the marker. (This was AIL-606 v6 — items stopped opening,
had to revert.)

## 4. Remove `<item>` from a real multi-choice quiz

The defect-7 fix is for ULTRA assignment surfaces (file upload + text
submission) only. If real multi-choice items live inside (any `<item>`
containing `<response_lid>`), removing them destroys the entire quiz.
`fix_ultra_qti_conflict.py` auto-skips these — but if you write your own
fix, replicate the skip.

## 5. Delete a "useless" disabled LINK

The LINK file must remain even when disabled — the chain between the
visible click-target and the underlying assessment passes through it. The
right move is to **flip the flag** (`ISAVAILABLE="true"`), not delete the
file. Deleting creates defect 6 (missing LINK), and the package's
internal consistency hides the breakage from defect-1 audits.

## 6. Single-line literal replace on `ISAVAILABLE`

```python
# WRONG — silently misses multi-line FLAGS XML cases
c = c.replace('<ISAVAILABLE value="false"/>', '<ISAVAILABLE value="true"/>')
```

Both single-line and multi-line forms can co-exist in the same archive.
Always use:

```python
# RIGHT
import re
c = re.sub(r'<ISAVAILABLE\s+value="false"\s*/>', '<ISAVAILABLE value="true"/>', c)
```

This was CAT-100 v2: 7 disabled LINKs, fixed 2, missed 5. Re-applied with
regex in v4.

## 7. Hand-build a new `<FORUM>` resource

Adding a module-specific Discussion forum requires `<FORUM>` payload +
`forumlink` wrapper + LINK + manifest declaration + item-tree placement —
**all five**. Doing this by hand risks ID collisions and broken chains.

The safe pattern: reuse the existing course-wide Discussion board and
adopt a subject-prefix convention in each module (`[M1 …]`, `[M2 …]`).

## 8. Bundle every fix into a single ZIP

Fixing every defect at once in v1 makes it impossible to trace what broke
when the next thing breaks. **One defect = one version**. The original AIL-606
fix path went v1 → v11; each step lets you diagnose and record exactly
what changed.

## 9. Ignore CDT/CST timezone

DUE date format: `2026-05-30 23:59:00 CDT`. From May to the first Sunday
of November the US Central zone is CDT (UTC-5); otherwise CST (UTC-6).
Summer term is all CDT. Blackboard's parser tolerates either, but
consistency is still better.

## 10. Try to recompute `.bb-package-sig`

This signature file can be ignored — Blackboard import does not validate
it, and you cannot recompute it without Blackboard's private key. Just
include it in the ZIP unchanged.

## 11. Skip the sandbox import

The most expensive failure mode. Sandbox import is the only way to verify
runtime behavior (defects 5, 6, 7). Click **every visible item** before
production. The audit script verifies structure, not click behavior.
