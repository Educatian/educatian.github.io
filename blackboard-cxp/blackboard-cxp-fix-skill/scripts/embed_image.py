"""
Embed an image (or any binary asset) into a Blackboard CXP package so it
renders inline in a content page.

Three things must happen together:
  1. Copy the asset file under csfiles/home_dir/ with __xid-NNNNNN_1.<ext> name
  2. Generate a sidecar XML at <same-path>.<ext>.xml
  3. Register a <resource> declaration in imsmanifest.xml

Then the content page body can reference it via Blackboard's @X@EmbeddedFile
syntax (build the <a data-bbfile="..." href="@X@..."> tag with this script's
helper, or copy the snippet from the docstring).

Usage:
  python embed_image.py /path/to/extracted/package /path/to/source.png \\
      --xid 992001_1 --title "Two Paths to Personal Website"
"""
import argparse
import os
import re
import shutil


SIDECAR_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<lom xmlns="http://www.imsglobal.org/xsd/imsmd_rootv1p2p1" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 \
imsmd_rootv1p2p1.xsd"><relation><resource><identifier>{xid}#/embedded/{name}\
</identifier></resource></relation></lom>'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('package_dir',
                    help='Path to the extracted CXP package directory')
    ap.add_argument('source',
                    help='Path to the source image/asset file')
    ap.add_argument('--xid', required=True,
                    help='High-numbered xid like 992001_1')
    ap.add_argument('--title', required=True,
                    help='Human-readable title for the manifest')
    args = ap.parse_args()

    ext = os.path.splitext(args.source)[1].lstrip('.')
    csf_home = os.path.join(args.package_dir, 'csfiles', 'home_dir')
    os.makedirs(csf_home, exist_ok=True)

    dst = os.path.join(csf_home, f'__xid-{args.xid}.{ext}')
    shutil.copy2(args.source, dst)

    sidecar = os.path.join(csf_home, f'__xid-{args.xid}.{ext}.xml')
    name = os.path.basename(args.source)
    open(sidecar, 'w', encoding='utf-8').write(
        SIDECAR_TEMPLATE.format(xid=args.xid, name=name)
    )

    # Register in manifest
    mp = os.path.join(args.package_dir, 'imsmanifest.xml')
    m = open(mp, encoding='utf-8').read()
    if f'identifier="csfile-{args.xid}"' in m:
        print(f'  manifest already has csfile-{args.xid}; skipping')
    else:
        decl = (
            f'<resource bb:file="csfiles/home_dir/__xid-{args.xid}.{ext}" '
            f'bb:title="{args.title}" identifier="csfile-{args.xid}" '
            f'type="webcontent" '
            f'xml:base="csfiles/home_dir/__xid-{args.xid}.{ext}"/>'
        )
        m = m.replace('</resources>', decl + '</resources>', 1)
        open(mp, 'w', encoding='utf-8').write(m)

    # Print the embed snippet the user can paste into a content page body
    print(f'\nInstalled at: {dst}')
    print(f'\nEmbed in a content page body using:')
    print(f'  <a data-bbid="img-{args.xid}" '
          f'data-bbfile="{{&quot;linkName&quot;:&quot;{name}&quot;,'
          f'&quot;mimeType&quot;:&quot;image/{ext}&quot;,'
          f'&quot;alternativeText&quot;:&quot;{args.title}&quot;,'
          f'&quot;isDecorative&quot;:false,'
          f'&quot;render&quot;:&quot;inline&quot;}}" '
          f'href="@X@EmbeddedFile.requestUrlStub@X@bbcswebdav/'
          f'xid-{args.xid}"></a>')


if __name__ == '__main__':
    main()
