"""Exercise both distributed CLI copies using only synthetic CXP resources."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [ROOT / "scripts/replace_body.py", ROOT / "blackboard-cxp-fix-skill/scripts/replace_body.py"]


class ReplaceBodyTests(unittest.TestCase):
    def test_html_backslashes_survive_the_xml_round_trip(self):
        bodies = [r'<p>Use C:\new\tools and \1 literally.</p>', r'<pre>\alpha + \beta &lt; 3</pre>']
        for script in SCRIPTS:
            for body in bodies:
                with self.subTest(script=script.relative_to(ROOT), body=body), tempfile.TemporaryDirectory() as fixture:
                    directory = Path(fixture)
                    resource = directory / "resource.dat"
                    html = directory / "body.html"
                    resource.write_text('<CONTENT><TEXT>Old body</TEXT><FLAGS value="keep"/></CONTENT>', encoding="utf-8")
                    html.write_text(body, encoding="utf-8")
                    result = subprocess.run([sys.executable, str(script), str(resource), str(html)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    parsed = ET.fromstring(resource.read_text(encoding="utf-8"))
                    self.assertEqual(parsed.findtext("TEXT"), body)
                    self.assertEqual(parsed.find("FLAGS").attrib, {"value": "keep"})


if __name__ == "__main__":
    unittest.main()
