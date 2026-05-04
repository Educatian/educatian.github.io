"""
Defect 5 fix — flip ISAVAILABLE=false → true on every LINK resource whose
REFERRER is a visible click-target (asmt-test-link / forumlink / courselink).

CRITICAL: uses regex with \\s+ between tag name and value= to handle the
multi-line FLAGS formatting that the naive single-line literal replace misses.

Usage:
  python fix_disabled_links.py /path/to/extracted/package
"""
import re
import os
import sys


def main(target_dir):
    files = sorted(p[:-4] for p in os.listdir(target_dir)
                   if p.startswith('res') and p.endswith('.dat'))

    def path(f):
        return os.path.join(target_dir, f + '.dat')

    def read(f):
        return open(path(f), encoding='utf-8', errors='replace').read()

    fixed = []
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
        if rfa and rfa.group(1) != 'true':
            continue  # referrer is hidden anyway; skip
        rfh = re.search(r'<CONTENTHANDLER\s+value="([^"]+)"', nrfc)
        rfh_val = rfh.group(1) if rfh else ''
        if not any(ch in rfh_val for ch in
                   ['asmt-test-link', 'forumlink', 'courselink']):
            continue

        # Apply the fix using whitespace-tolerant regex
        new_c = re.sub(
            r'<ISAVAILABLE\s+value="false"\s*/>',
            '<ISAVAILABLE value="true"/>',
            c,
            count=1,
        )
        # Optionally blank legacy "New Assignment 1/24/25" titles
        new_c = re.sub(
            r'<TITLE\s+value="New Assignment[^"]*"\s*/>',
            '<TITLE value=""/>',
            new_c,
            count=1,
        )
        if new_c != c:
            open(path(f), 'w', encoding='utf-8').write(new_c)
            fixed.append((f, rf, rfh_val))

    print(f'Fixed {len(fixed)} disabled LINK resources:')
    for link, referrer, handler in fixed:
        print(f'  {link} -> referrer={referrer} ({handler})')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python fix_disabled_links.py /path/to/extracted/package')
        sys.exit(2)
    main(sys.argv[1])
