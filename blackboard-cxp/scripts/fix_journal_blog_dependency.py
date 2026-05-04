"""
Defect 2 fix — remove dependencies on Blackboard tools ULTRA does not support
(Journal, Blog, Wiki). The visible content item is converted into a regular
document; the tool-data resource and its LINK are deleted; manifest is
cleaned.

Trigger: import log shows "<Tool> aren't supported at this time and were
removed" + "The content item failed to convert."

Usage:
  python fix_journal_blog_dependency.py /path/to/extracted/package
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

    retired_handlers = {
        'resource/x-bb-journallink': 'journal',
        'resource/x-bb-bloglink':    'blog',
        'resource/x-bb-wikilink':    'wiki',
    }

    # Step 1: find CONTENT items using a retired handler
    content_to_fix = []
    for f in files:
        if f in ('res00009', 'res00010'):
            continue  # skip handler registry
        c = read(f)
        if '<CONTENT' not in c:
            continue
        nc = re.sub(r'\s+', ' ', c)
        h = re.search(r'<CONTENTHANDLER\s+value="([^"]+)"', nc)
        if not h or h.group(1) not in retired_handlers:
            continue
        content_to_fix.append((f, h.group(1)))

    print(f'Found {len(content_to_fix)} CONTENT items using retired handlers:')
    for f, h in content_to_fix:
        print(f'  {f}: {h}')

    # Step 2: walk LINK and tool-data to delete
    to_delete_files = set()
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
        referrer_map.setdefault(rf.group(1), []).append(f)

    for content_id, handler in content_to_fix:
        # Find LINKs that REFERRER from this CONTENT
        for link in referrer_map.get(content_id, []):
            link_c = read(link)
            nlc = re.sub(r'\s+', ' ', link_c)
            rt = re.search(
                r'<REFERREDTO\s+id="(res[0-9]+)"\s+type="([^"]+)"',
                nlc,
            )
            if not rt:
                continue
            target_id, target_type = rt.group(1), rt.group(2)
            if target_type in ('BLOG_JOURNAL', 'BLOG', 'WIKI', 'JOURNAL'):
                to_delete_files.add(link)
                to_delete_files.add(target_id)

        # Step 3: change CONTENTHANDLER + RENDERTYPE on the CONTENT item itself
        c = read(content_id)
        c = re.sub(
            r'<CONTENTHANDLER\s+value="resource/x-bb-(journallink|bloglink|wikilink)"',
            '<CONTENTHANDLER value="resource/x-bb-document"',
            c,
        )
        c = re.sub(
            r'<RENDERTYPE\s+value="LINK"\s*/>',
            '<RENDERTYPE value="REGULAR"/>',
            c,
        )
        open(path(content_id), 'w', encoding='utf-8').write(c)
        print(f'  {content_id}: handler→document, rendertype→REGULAR')

    # Step 4: delete tool-data files and LINK files
    for fid in sorted(to_delete_files):
        fp = path(fid)
        if os.path.exists(fp):
            os.remove(fp)
            print(f'  deleted {fid}.dat')

    # Step 5: strip declarations from manifest
    mp = os.path.join(target_dir, 'imsmanifest.xml')
    m = open(mp, encoding='utf-8').read()
    for fid in sorted(to_delete_files):
        pat = re.compile(
            r'<resource\b[^>]*?bb:file="' + fid + r'\.dat"[^>]*?/>',
            re.DOTALL,
        )
        new_m, n = pat.subn('', m)
        if n > 0:
            m = new_m
            print(f'  stripped manifest decl: {fid}')
    open(mp, 'w', encoding='utf-8').write(m)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python fix_journal_blog_dependency.py '
              '/path/to/extracted/package')
        sys.exit(2)
    main(sys.argv[1])
