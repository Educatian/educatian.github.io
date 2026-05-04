"""
Defect 7 fix — silence access-code logs by emptying the QTI section on
ULTRA-marked asmt-test-link items.

CRITICAL preconditions before applying:
  1. The wrapper has ULTRA_ASSESSMENT_MARKER=true
  2. The wrapper's CONTENTHANDLER is asmt-test-link
  3. The intended student experience is ULTRA assignment surface
     (file upload + text submission), NOT classic test taking with questions

DO NOT apply this fix to genuine multi-question quizzes (e.g., MC tests where
the student is supposed to answer questions). Removing the items would destroy
the quiz content.

Usage:
  python fix_ultra_qti_conflict.py /path/to/orig /path/to/cur

The script copies orig QTI files (which have empty <section>) over cur QTI
files (which have a Codex-added <item>) for each ULTRA-marked wrapper.
"""
import re
import os
import sys
import shutil


def main(orig_dir, cur_dir):
    files = sorted(p[:-4] for p in os.listdir(cur_dir)
                   if p.startswith('res') and p.endswith('.dat'))

    def cur_read(f):
        return open(os.path.join(cur_dir, f + '.dat'),
                    encoding='utf-8', errors='replace').read()

    # Build referrer map for cur
    referrer_map = {}
    for f in files:
        c = cur_read(f)
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

    # Find ULTRA-marked asmt-test-link wrappers and walk to their QTI files
    qti_to_revert = set()
    for f in files:
        c = cur_read(f)
        if 'ULTRA_ASSESSMENT_MARKER' not in c:
            continue
        if 'asmt-test-link' not in c:
            continue
        for link in referrer_map.get(f, []):
            if link['avail'] != 'true':
                continue
            link_c = cur_read(link['link'])
            nlc = re.sub(r'\s+', ' ', link_c)
            rt = re.search(
                r'<REFERREDTO\s+id="(res[0-9]+)"\s+type="COURSE_ASSESSMENT"',
                nlc,
            )
            if not rt:
                continue
            try:
                ca = cur_read(rt.group(1))
            except FileNotFoundError:
                continue
            a = re.search(r'ASMTID\s+value="([^"]+)"', ca)
            if not a:
                continue
            qti_id = a.group(1)
            try:
                qti = cur_read(qti_id)
            except FileNotFoundError:
                continue
            # Only revert if QTI has <item> inside <section> (Codex-added)
            if re.search(r'<section\b[^>]*>.*?<item\b', qti, re.DOTALL):
                qti_to_revert.add(qti_id)

    print(f'QTI files to revert (ULTRA-marker wrappers with non-empty section):'
          f' {len(qti_to_revert)}')

    for q in sorted(qti_to_revert):
        src = os.path.join(orig_dir, q + '.dat')
        dst = os.path.join(cur_dir, q + '.dat')
        if not os.path.exists(src):
            print(f'  WARN: orig {q}.dat not found; skipping')
            continue
        # Sanity-check: orig QTI should have empty <section>
        orig_qti = open(src, encoding='utf-8', errors='replace').read()
        if re.search(r'<section\b[^>]*>.*?<item\b', orig_qti, re.DOTALL):
            print(f'  WARN: orig {q}.dat ALSO has <item> in <section>; '
                  'this may be a real classic quiz, NOT an ULTRA assignment. '
                  'Skipping. Inspect manually.')
            continue
        shutil.copy2(src, dst)
        print(f'  reverted {q}.dat to orig empty-section form')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python fix_ultra_qti_conflict.py '
              '/path/to/orig /path/to/cur')
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
