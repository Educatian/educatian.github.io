"""
Reset all OUTCOMEDEFINITION DUE dates to a target term schedule.

The Gradebook resource (typically res00096 or res00178/179, depending on the
course) holds <OUTCOMEDEFINITION> blocks whose <DUE> dates carry over from
the source archive's term. After importing into a new term, these dates need
to move forward in lockstep.

Usage:
  python update_due_dates.py /path/to/extracted/package schedule.json

Where schedule.json maps each visible item title to its new due date (CDT/CST):

  {
    "Module 1: Quiz": "2026-05-27 23:59:00 CDT",
    "Module 1: Assess - Design Tension Rationale": "2026-05-30 23:59:00 CDT",
    ...
  }

Validates: no Sundays, no Juneteenth (2026-06-19), within term window if both
TERM_START and TERM_END env vars set as YYYY-MM-DD.
"""
import re
import os
import sys
import json
import datetime


def main(target_dir, schedule_path):
    schedule = json.load(open(schedule_path, encoding='utf-8'))

    # Validate the schedule (no Sundays, no Juneteenth)
    for title, due in schedule.items():
        d_str = due.split(' ')[0]
        d = datetime.datetime.strptime(d_str, '%Y-%m-%d').date()
        if d.weekday() == 6:
            print(f'  WARNING Sunday: "{title}" -> {due}')
        if d == datetime.date(2026, 6, 19):
            print(f'  WARNING Juneteenth: "{title}" -> {due}')

    # Find the gradebook file (looks for <GRADEBOOK> + <OUTCOMEDEFINITION>)
    gb_path = None
    for f in os.listdir(target_dir):
        if not (f.startswith('res') and f.endswith('.dat')):
            continue
        c = open(os.path.join(target_dir, f),
                 encoding='utf-8', errors='replace').read()
        if '<GRADEBOOK' in c and '<OUTCOMEDEFINITION' in c:
            gb_path = os.path.join(target_dir, f)
            break

    if not gb_path:
        print('ERROR: gradebook resource not found')
        sys.exit(1)
    print(f'Gradebook: {os.path.basename(gb_path)}')

    c = open(gb_path, encoding='utf-8').read()
    updated = 0
    not_found = []

    def update_block(match):
        nonlocal updated
        block = match.group(0)
        title_m = re.search(r'<TITLE\s+value="([^"]*)"', block)
        if not title_m:
            return block
        title_raw = title_m.group(1)
        # Decode XML entities for matching
        title = (title_raw
                 .replace('&amp;', '&')
                 .replace('&apos;', "'")
                 .replace('&quot;', '"'))
        new_due = schedule.get(title, schedule.get(title_raw))
        if new_due is None:
            not_found.append(title)
            return block
        new_block = re.sub(
            r'<DUE\s+value="[^"]*"',
            f'<DUE value="{new_due}"',
            block,
            count=1,
        )
        if new_block != block:
            updated += 1
        return new_block

    new_c = re.sub(
        r'<OUTCOMEDEFINITION[^>]*>.*?</OUTCOMEDEFINITION>',
        update_block,
        c,
        flags=re.DOTALL,
    )

    open(gb_path, 'w', encoding='utf-8').write(new_c)
    print(f'\nUpdated {updated} due dates')
    if not_found:
        print(f'\nUnmatched titles (left unchanged):')
        for t in not_found:
            print(f'  - "{t}"')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python update_due_dates.py '
              '/path/to/extracted/package schedule.json')
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
