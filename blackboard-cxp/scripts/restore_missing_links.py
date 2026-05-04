"""
Defect 6 fix — restore LINK resources that were stripped from the package
(both file and manifest declaration removed in lockstep, so the convert-time
audit cannot detect them).

Strategy: compare current package against a pristine archive of the same
course. For every LINK in orig that is missing from cur AND whose REFERRER
is a visible click-target item, restore the LINK file with ISAVAILABLE=true.

Usage:
  python restore_missing_links.py /path/to/orig /path/to/cur
"""
import re
import os
import sys
import shutil


def find_links(target_dir):
    """Return dict of LINK resource id -> info."""
    links = {}
    for f in sorted(os.listdir(target_dir)):
        if not (f.startswith('res') and f.endswith('.dat')):
            continue
        c = open(os.path.join(target_dir, f),
                 encoding='utf-8', errors='replace').read()
        if not re.search(r'<LINK[\s>]', c):
            continue
        if 'REFERRER' not in c:
            continue
        nc = re.sub(r'\s+', ' ', c)
        rf = re.search(r'<REFERRER\s+id="(res[0-9]+)"', nc)
        rt = re.search(
            r'<REFERREDTO\s+id="(res[0-9]+)"\s+type="([^"]+)"',
            nc,
        )
        if not rf or not rt:
            continue
        avail = re.search(r'<ISAVAILABLE\s+value="([^"]+)"', nc)
        links[f[:-4]] = {
            'avail': avail.group(1) if avail else 'true',
            'from': rf.group(1),
            'to': rt.group(1),
            'to_type': rt.group(2),
        }
    return links


def main(orig_dir, cur_dir):
    orig_links = find_links(orig_dir)
    cur_links = find_links(cur_dir)

    missing_in_cur = sorted(set(orig_links) - set(cur_links))
    print(f'orig LINKs={len(orig_links)} cur LINKs={len(cur_links)} '
          f'missing in cur={len(missing_in_cur)}')

    # Filter to LINKs whose REFERRER is a visible click-target
    click_handlers = {
        'resource/x-bb-asmt-test-link',
        'resource/x-bb-forumlink',
        'resource/x-bb-courselink',
    }
    to_restore = {}
    for link in missing_in_cur:
        info = orig_links[link]
        ref = info['from']
        rp = os.path.join(cur_dir, ref + '.dat')
        if not os.path.exists(rp):
            continue
        rc = open(rp, encoding='utf-8', errors='replace').read()
        if '<CONTENT' not in rc:
            continue
        nrc = re.sub(r'\s+', ' ', rc)
        h = re.search(r'<CONTENTHANDLER\s+value="([^"]+)"', nrc)
        if not h or h.group(1) not in click_handlers:
            continue
        a = re.search(r'<ISAVAILABLE\s+value="([^"]+)"', nrc)
        if a and a.group(1) != 'true':
            continue
        to_restore[link] = (ref, info['to'], info['to_type'])

    print(f'\nLINKs to restore (referrer is visible click-target): '
          f'{len(to_restore)}')

    # Verify REFERREDTO targets exist in cur
    missing_targets = []
    for link, (ref, target, ttype) in to_restore.items():
        if not os.path.exists(os.path.join(cur_dir, target + '.dat')):
            missing_targets.append(target)

    # Restore missing target files from orig
    for t in missing_targets:
        src = os.path.join(orig_dir, t + '.dat')
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(cur_dir, t + '.dat'))
            print(f'  restored target {t}.dat from orig')

    # Restore LINK files with ISAVAILABLE=true
    for link in to_restore:
        c = open(os.path.join(orig_dir, link + '.dat'),
                 encoding='utf-8').read()
        c = re.sub(
            r'<ISAVAILABLE\s+value="false"\s*/>',
            '<ISAVAILABLE value="true"/>',
            c,
        )
        c = re.sub(
            r'<TITLE\s+value="New Assignment[^"]*"\s*/>',
            '<TITLE value=""/>',
            c,
        )
        open(os.path.join(cur_dir, link + '.dat'), 'w',
             encoding='utf-8').write(c)
        print(f'  {link}.dat restored ({len(c)} chars)')

    # Update manifest with new declarations
    m_orig = open(os.path.join(orig_dir, 'imsmanifest.xml'),
                  encoding='utf-8').read()
    m_cur_path = os.path.join(cur_dir, 'imsmanifest.xml')
    m_cur = open(m_cur_path, encoding='utf-8').read()

    def get_decl(m, ident):
        pat = re.compile(
            r'<resource\b[^>]*?bb:file="' + ident + r'\.dat"[^>]*?/>',
            re.DOTALL,
        )
        return pat.search(m)

    declared = []
    for link in list(to_restore) + missing_targets:
        if f'identifier="{link}"' in m_cur:
            continue
        decl = get_decl(m_orig, link)
        if decl:
            m_cur = m_cur.replace(
                '</resources>',
                decl.group(0) + '</resources>',
                1,
            )
            declared.append(link)

    if declared:
        open(m_cur_path, 'w', encoding='utf-8').write(m_cur)
        print(f'\nManifest updated with {len(declared)} new declarations')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python restore_missing_links.py '
              '/path/to/orig /path/to/cur')
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
