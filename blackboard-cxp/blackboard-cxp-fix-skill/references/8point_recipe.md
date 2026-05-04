# 8-Point Defect Recipe

Reference card. Use this together with `audit_8point.py` (which mechanically
checks every class).

## 1. Orphan manifest declarations  &nbsp;`CONVERT`

The manifest declares a `<resource>` whose `bb:file` points at a `.dat` that
does not exist (or vice versa).

**Detect:**
```bash
comm -23 \
  <(grep -oE 'identifier="res[0-9]+"' imsmanifest.xml | sort -u) \
  <(ls *.dat | sed 's/\.dat$//' | sort -u)
```

**Fix:** restore the missing `.dat` from the original archive, OR strip the
`<resource>` declaration from the manifest.

## 2. Retired-tool handlers (Journal / Blog / Wiki)  &nbsp;`CONVERT`

Blackboard ULTRA does not support Journal, Blog, or Wiki. A
`<CONTENTHANDLER value="resource/x-bb-journallink"/>` triggers
`"Reflective Journal — Blogs aren't supported"` and silently drops the
content.

**Fix (`fix_journal_blog_dependency.py`):**
1. Change the visible CONTENT's `CONTENTHANDLER` to `resource/x-bb-document`
   and `RENDERTYPE` to `REGULAR`.
2. Delete the tool-data `.dat` file (BLOG/JOURNAL/WIKI payload).
3. Delete the LINK file that connected them.
4. Strip both deletions' `<resource>` declarations from the manifest.

## 3. Wrong-type substitution  &nbsp;`CONVERT`

The manifest's declared `bb:type` does not match the `.dat` file's actual
root XML element. E.g., manifest says `course/x-bb-coursemessagefolder`
but the file's root is `<questestinterop>`.

**Fix:** restore the `.dat` from the original. Do **not** overwrite an
existing resource ID with a different-type payload — issue a fresh ID.

## 4. Empty leaf content items  &nbsp;`CONVERT`

A student-visible `<CONTENT>` that has all of:
- `<DESCRIPTION value=""/>` (empty)
- `<TEXT/>` (empty body)
- `ISFOLDER="false"`
- no `<FILES><FILE>` either

**False positives to skip:**
- `asmt-test-link` / `forumlink` / `courselink` wrappers (intentionally
  empty — they point via LINK)
- `ULTRA_ASSESSMENT_MARKER=true` items (that's defect 7's territory)
- `resource/x-bb-folder` / `x-bb-lesson` (folders themselves)

**Fix:** restore body from the original, OR change type to folder, OR add
minimum content.

## 5. Disabled LINK resources  &nbsp;`RUNTIME`

A `<LINK>` between a visible click-target and the underlying assessment is
flagged `<ISAVAILABLE value="false"/>`. The item imports cleanly, the
gradebook column gets created, but clicking it does **nothing**.

**Origin:** instructor pre-built the assignment in a prior term and disabled
it until release; the disabled flag carries through the export.

**Fix (`fix_disabled_links.py`):**
```python
import re
c = re.sub(
    r'<ISAVAILABLE\s+value="false"\s*/>',
    '<ISAVAILABLE value="true"/>',
    c,
)
```

## 6. Missing LINK resources  &nbsp;`RUNTIME`

More severe than 5: both the LINK file AND its manifest declaration were
stripped together. The package stays internally consistent (no orphan
declarations), so defect 1's audit cannot detect it. A separate
visible-click-target ↔ LINK match check is needed.

**Fix (`restore_missing_links.py`):** restore the LINK file from the original
archive, flip `ISAVAILABLE=true`, add the declaration to the manifest.

## 7. ULTRA marker × classic-QTI conflict  &nbsp;`RUNTIME`

The hardest case. An asmt-test-link item carries
`<EXTENDEDDATA><ENTRY key="ULTRA_ASSESSMENT_MARKER">true</ENTRY></EXTENDEDDATA>`
AND the questestinterop file at the end of its LINK chain has `<item>`
content inside its `<section>`.

**Symptom:** the item opens normally, but every render appends a sequential
entry to the server log: `260504/_666818_1/3.log`, `4.log`, `5.log`, …

**Root cause:** the marker tells ULTRA "render as ULTRA-native assignment
surface (file upload + text submission)," but the underlying QTI is in the
classic Blackboard test format. ULTRA bridges the two models on every render
and emits a conversion-trace entry.

**Fix (`fix_ultra_qti_conflict.py`):** remove every `<item>` from inside the
QTI body's `<section>`. Keep the marker. Empty section = "this is a ULTRA
assignment; don't try to convert classic questions."

```xml
<questestinterop>
  <assessment title="...">
    <assessmentmetadata>...</assessmentmetadata>
    <rubric>...</rubric>
    <presentation_material>...</presentation_material>
    <section>
      <sectionmetadata>...</sectionmetadata>
      <!-- Must be empty; no <item> -->
    </section>
  </assessment>
</questestinterop>
```

**HARD RULE — do not apply to real quizzes.** If real multiple-choice
items live inside (any `<item>` containing `<response_lid>`), removing them
destroys the quiz. The fix script auto-skips these.

**The v6 failure case (do not repeat):** if you try to silence the
access-code log by removing the ULTRA marker itself, the item stops opening.
The marker is the trigger for ULTRA rendering. Empty the QTI body, not the
marker.

## 8. Whitespace-tolerant ISAVAILABLE replace  &nbsp;`TOOLING`

The most common trap when writing fix scripts for defects 5/6. Blackboard's
LINK XML appears in two formats inside the same archive:

```
Single-line:
<FLAGS><ISAVAILABLE value="false"/></FLAGS>

Multi-line:
<FLAGS><ISAVAILABLE
  value="false"/></FLAGS>
```

**Wrong** (silently misses multi-line):
```python
c = c.replace('<ISAVAILABLE value="false"/>', '<ISAVAILABLE value="true"/>')
```

**Right:**
```python
import re
c = re.sub(r'<ISAVAILABLE\s+value="false"\s*/>', '<ISAVAILABLE value="true"/>', c)
```

Apply the same whitespace-tolerance principle when matching any XML
attribute that might span lines.
