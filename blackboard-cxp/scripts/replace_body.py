"""
Replace the HTML body inside a Blackboard CXP <CONTENT> resource without
disturbing anything else (DATES, FLAGS, CONTENTHANDLER, PARENTID, …).

Blackboard stores the rendered HTML body inside <TEXT>...</TEXT>, with all
HTML tags entity-encoded ('<' → '&lt;'). This helper handles the encoding
round-trip safely.

Usage:
  python replace_body.py path/to/resNNNNN.dat path/to/new_body.html

new_body.html should contain raw HTML; this script will entity-encode it
before writing to the resource file.
"""
import re
import sys
import argparse


def html_entity_encode(s):
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;')
             .replace("'", '&apos;'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('res_file',
                    help='Path to the resNNNNN.dat file to modify')
    ap.add_argument('html_file',
                    help='Path to the HTML file with the new body content')
    ap.add_argument('--updated',
                    default=None,
                    help='Optional new <UPDATED> timestamp '
                         '(YYYY-MM-DD HH:MM:SS CDT). If omitted, leaves it alone.')
    args = ap.parse_args()

    new_html = open(args.html_file, encoding='utf-8').read()
    encoded = html_entity_encode(new_html)

    c = open(args.res_file, encoding='utf-8').read()
    if not re.search(r'<TEXT>.*?</TEXT>', c, re.DOTALL):
        print(f'ERROR: no <TEXT>...</TEXT> in {args.res_file}')
        sys.exit(1)
    c2 = re.sub(
        r'<TEXT>.*?</TEXT>',
        f'<TEXT>{encoded}</TEXT>',
        c,
        count=1,
        flags=re.DOTALL,
    )
    if args.updated:
        c2 = re.sub(
            r'<UPDATED\s+value="[^"]+"',
            f'<UPDATED value="{args.updated}"',
            c2,
            count=1,
        )
    open(args.res_file, 'w', encoding='utf-8').write(c2)
    print(f'Replaced body of {args.res_file} '
          f'({len(new_html)} html chars → {len(encoded)} encoded chars)')


if __name__ == '__main__':
    main()
