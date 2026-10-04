"""Run the unit tests and save a readable report to ../test_results.txt

Usage (from the folder that contains manage.py):
    python make_test_report.py
"""
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import django

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent / "test_results.txt"
LINE = "=" * 70
THIN = "-" * 70

# Run the tests with one line of output per test
result = subprocess.run(
    [sys.executable, "manage.py", "test", "note", "--verbosity", "2"],
    cwd=HERE,
    capture_output=True,
    text=True,
    encoding="utf-8",
)
output = result.stderr + result.stdout

# Collect (area, test name, outcome) for every test line
pattern = r"^(test\w+) \(note\.tests\.(\w+)(?:\.\w+)?\) \.\.\. (\w+)$"
areas = {}
for name, area, outcome in re.findall(pattern, output, re.MULTILINE):
    area = re.sub(r"(?<!^)(?=[A-Z])", " ", area)
    nice_name = name.replace("test_", "", 1).replace("_", " ")
    areas.setdefault(area, []).append((nice_name, outcome))

total = sum(len(tests) for tests in areas.values())
passed = sum(o == "ok" for tests in areas.values() for _, o in tests)
problems = total - passed
seconds = re.search(r"Ran \d+ tests? in ([\d.]+)s", output)
python_version = "%d.%d.%d" % sys.version_info[:3]

if problems == 0 and total > 0:
    verdict = "ALL TESTS PASSED"
else:
    verdict = "SOME TESTS FAILED"

lines = [
    LINE,
    " STICKY NOTES - UNIT TEST REPORT",
    LINE,
    " Date    : " + datetime.now().strftime("%Y-%m-%d %H:%M"),
    " Python  : " + python_version,
    " Django  : " + django.get_version(),
    " Command : python manage.py test note",
    THIN,
    " RESULT  : %s  (%d passed, %d failed)" % (verdict, passed, problems),
    " Time    : %s seconds" % (seconds.group(1) if seconds else "?"),
    LINE,
    "",
    "SUMMARY BY AREA",
    THIN,
]

width = max(len(area) for area in areas) if areas else 0
for area, tests in areas.items():
    ok = sum(o == "ok" for _, o in tests)
    lines.append(" %-*s  %2d / %2d passed" % (width, area, ok, len(tests)))

lines += ["", "", "ALL TESTS", THIN]
for area, tests in areas.items():
    lines += ["", area.upper()]
    for nice_name, outcome in tests:
        mark = "[PASS]" if outcome == "ok" else "[FAIL]"
        lines.append("  %s %s" % (mark, nice_name))

# If anything failed, keep Django's own error details at the end
if problems > 0 or total == 0:
    lines += ["", "", "DETAILS OF PROBLEMS", THIN, output.strip()]

lines.append("")
REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
print(verdict + " - report saved to " + str(REPORT))
sys.exit(0 if problems == 0 and total > 0 else 1)
