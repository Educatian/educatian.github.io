"""
8-point Blackboard ULTRA import recipe audit.

Run after extracting your CXP package to a directory containing:
  imsmanifest.xml
  res00001.dat ... resNNNNNN.dat
  csfiles/...

Usage:
  python audit_8point.py /path/to/extracted/package

Prints PASS/FAIL for each of the 8 defect classes catalogued in the
2026-05-04 fix marathon. Exit code 0 if all PASS, 1 otherwise.
"""
import re
import os
import sys


def main(target_dir):
    files = sorted(p[:-4] for p in os.listdir(target_dir)
                   if p.startswith('res') and p.endswith('.dat'))
    manifest = open(os.path.join(target_dir, 'imsmanifest.xml'),
                    encoding='utf-8').read()

    def read(f):
        return open(os.path.join(target_dir, f + '.dat'),
                    encoding='utf-8', errors='replace').read()

    results = []

    # Defect 1: orphan manifest declarations
    decls = sorted(set(re.findall(r'identifier="(res[0-9]+)"', manifest)))
    file_set = set(files)
    missing = [r for r in decls if r not in file_set]
    orphan = [f for f in files if f not in decls]
    results.append((
        '1. Orphan manifest decls',
        not missing and not orphan,
        f'decls={len(decls)} files={len(files)} missing={len(missing)} orphan={len(orphan)}',
    ))

    # Defect 2: retired-tool handlers (journal/blog/wiki) in actual content
    retired = ['x-bb-journallink', 'x-bb-bloglink', 'x-bb-wikilink']
    hits = []
    for f in files:
        # res00010 (or equivalent) is the content-handler registry; skip
        if f in ('res00009', 'res00010'):
            continue
        c = read(f)
        for h in retired:
            if h in c and '<CONTENT' in c:
                hits.append((f, h))
    results.append((
        '2. Retired-tool handlers in CONTENT',
        not hits,
        f'hits={len(hits)} {hits[:5]}',
    ))

    # Defect 3: wrong-type substitution (manifest type vs root XML element)
    type_violations = []
    for f in files:
        c = read(f)
        mp = re.search(r'identifier="' + f + r'"[^/]*type="([^"]+)"', manifest)
        if not mp:
            continue
        declared = mp.group(1)
        nc = c.lstrip('﻿').lstrip()
        nc = re.sub(r'<\?xml[^?]*\?>', '', nc).lstrip()
        root_match = re.match(r'<([A-Z]+|[a-z]+)\b', nc)
        if not root_match:
            continue
        root = root_match.group(1)
        if declared == 'course/x-bb-coursemessagefolder' and root != 'COURSEMESSAGEFOLDERS':
            type_violations.append((f, declared, root))
        if declared == 'resource/x-bb-blog' and root != 'BLOG':
            type_violations.append((f, declared, root))
    results.append((
        '3. Wrong-type substitution',
        not type_violations,
        f'violations={len(type_violations)} {type_violations}',
    ))

    # Defect 4: empty leaf content items (refined to skip legitimate empty wrappers)
    intentionally_empty_handlers = {
        'resource/x-bb-folder', 'resource/x-bb-lesson',
        'resource/x-bb-asmt-test-link', 'resource/x-bb-asmt-survey-link',
        'resource/x-bb-forumlink', 'resource/x-bb-courselink',
        'resource/x-bb-externallink', 'resource/x-bb-blti-link',
    }
    empty_leaves = []
    for f in files:
        c = read(f)
        if '<CONTENT' not in c:
            continue
        if not re.search(r'DESCRIPTION\s+value=""', c):
            continue
        if '<TEXT/>' not in c:
            continue
        if 'ISFOLDER value="true"' in c:
            continue
        if '<FILES><FILE' in c:
            continue
        nc = re.sub(r'\s+', ' ', c)
        h = re.search(r'<CONTENTHANDLER\s+value="([^"]+)"', nc)
        if h and h.group(1) in intentionally_empty_handlers:
            continue
        if 'ULTRA_ASSESSMENT_MARKER' in c:
            continue
        if h and 'bltiplacement' in h.group(1):
            continue
        title = re.search(r'TITLE value="([^"]*)"', c)
        empty_leaves.append((
            f,
            title.group(1) if title else '?',
            h.group(1) if h else '?',
        ))
    results.append((
        '4. Empty leaf content items',
        not empty_leaves,
        f'leaves={len(empty_leaves)} {empty_leaves[:5]}',
    ))

    # Build LINK referrer map for defects 5/6/7
    referrer_map = {}
    for f in files:
        c = read(f)
        if not re.search(r'<LINK[\s>]', c):
            continue
        if 'REFERRER' not in c:
            continue
        nc = re.sub(r'\s+', ' ', c)
        rf = re.search(r'<REFERRER\s+id="(res[0-9]+)"', nc)
        if not rf:
            continue
        avail = re.search(r'<ISAVAILABLE\s+value="([^"]+)"', nc)
        avail_val = avail.group(1) if avail else 'true'
        referrer_map.setdefault(rf.group(1), []).append({
            'link': f, 'avail': avail_val,
        })

    # Defect 5: disabled LINK with visible click-target referrer
    disabled = []
    for f in files:
        c = read(f)
        if not re.search(r'<LINK[\s>]', c):
            continue
        if 'REFERRER' not in c:
            continue
        nc = re.sub(r'\s+', ' ', c)
        if not re.search(r'<ISAVAILABLE\s+value="false"\s*/>', nc):
            continue
        rf_m = re.search(r'<REFERRER\s+id="(res[0-9]+)"', nc)
        if not rf_m:
            continue
        rf = rf_m.group(1)
        try:
            rf_c = read(rf)
        except FileNotFoundError:
            continue
        nrfc = re.sub(r'\s+', ' ', rf_c)
        rfa = re.search(r'<ISAVAILABLE\s+value="([^"]+)"', nrfc)
        rfa_val = rfa.group(1) if rfa else 'true'
        rfh = re.search(r'<CONTENTHANDLER\s+value="([^"]+)"', nrfc)
        rfh_val = rfh.group(1) if rfh else ''
        click_handlers = ['asmt-test-link', 'forumlink', 'courselink']
        if rfa_val == 'true' and any(ch in rfh_val for ch in click_handlers):
            disabled.append((f, rf, rfh_val))
    results.append((
        '5. Disabled LINKs blocking visible items',
        not disabled,
        f'disabled={len(disabled)} {disabled[:5]}',
    ))

    # Defect 6: visible click-target with NO available LINK
    orphan_clicks = []
    click_handlers_set = {
        'resource/x-bb-asmt-test-link',
        'resource/x-bb-forumlink',
        'resource/x-bb-courselink',
    }
    for f in files:
        c = read(f)
        if '<CONTENT' not in c:
            continue
        nc = re.sub(r'\s+', ' ', c)
        h = re.search(r'<CONTENTHANDLER\s+value="([^"]+)"', nc)
        if not h or h.group(1) not in click_handlers_set:
            continue
        a = re.search(r'<ISAVAILABLE\s+value="([^"]+)"', nc)
        if a and a.group(1) != 'true':
            continue
        avail_links = [l for l in referrer_map.get(f, [])
                       if l['avail'] == 'true']
        if not avail_links:
            title = re.search(r'TITLE value="([^"]*)"', c)
            orphan_clicks.append((
                f,
                title.group(1) if title else '?',
                h.group(1),
            ))
    results.append((
        '6. Click-targets without available LINK',
        not orphan_clicks,
        f'orphan_clicks={len(orphan_clicks)} {orphan_clicks[:5]}',
    ))

    # Defect 7: ULTRA-marker x classic-QTI conflict
    problems = []
    for f in files:
        c = read(f)
        if 'ULTRA_ASSESSMENT_MARKER' not in c:
            continue
        if 'asmt-test-link' not in c:
            continue
        avail_links = [l for l in referrer_map.get(f, [])
                       if l['avail'] == 'true']
        for link in avail_links:
            link_c = read(link['link'])
            nlc = re.sub(r'\s+', ' ', link_c)
            rt = re.search(
                r'<REFERREDTO\s+id="(res[0-9]+)"\s+type="COURSE_ASSESSMENT"',
                nlc,
            )
            if not rt:
                continue
            try:
                ca = read(rt.group(1))
            except FileNotFoundError:
                continue
            a = re.search(r'ASMTID\s+value="([^"]+)"', ca)
            if not a:
                continue
            qti_id = a.group(1)
            try:
                qti = read(qti_id)
            except FileNotFoundError:
                continue
            has_item = bool(
                re.search(r'<section\b[^>]*>.*?<item\b', qti, re.DOTALL)
            )
            if has_item:
                title = re.search(r'TITLE\s+value="([^"]*)"', c)
                problems.append((
                    f, qti_id,
                    title.group(1) if title else '?',
                ))
    results.append((
        '7. ULTRA-marker x classic-QTI conflict',
        not problems,
        f'conflicts={len(problems)} {problems[:5]}',
    ))

    # Defect 8: Whitespace-tolerant ISAVAILABLE check (regex coverage)
    # If defect 5 used a regex with \s+ tolerance, this should always be 0.
    # We re-check with both single-line literal and multi-line regex to ensure
    # nothing got missed.
    multiline_misses = 0
    for f in files:
        c = read(f)
        if not re.search(r'<LINK[\s>]', c):
            continue
        # Find ISAVAILABLE that the literal-string replace would NOT hit
        # but the regex would.
        literal_count = c.count('<ISAVAILABLE value="false"/>')
        regex_count = len(re.findall(r'<ISAVAILABLE\s+value="false"\s*/>', c))
        if regex_count > literal_count:
            multiline_misses += (regex_count - literal_count)
    results.append((
        '8. Whitespace-tolerant ISAVAILABLE coverage',
        multiline_misses == 0,
        f'multiline_misses={multiline_misses}',
    ))

    print('=' * 70)
    print(f'8-Point Blackboard ULTRA Import Recipe Audit  --  {target_dir}')
    print('=' * 70)
    all_pass = True
    for label, ok, detail in results:
        flag = 'PASS' if ok else 'FAIL'
        print(f'  [{flag}] {label}')
        print(f'         {detail}')
        if not ok:
            all_pass = False
    print()
    print('Overall:', 'ALL PASS' if all_pass else 'NEEDS WORK')
    return 0 if all_pass else 1


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python audit_8point.py /path/to/extracted/package')
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
