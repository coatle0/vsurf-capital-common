import importlib.util
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "report_validator.py"
SPEC = importlib.util.spec_from_file_location("report_validator", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


GOOD_REPORT = (
    "# ORDER 999 — smoke\n\n"
    "- 상태: DONE\n"
    "- 좌표: N/A\n"
    "- PC1 경로: C:\\lab\\vsurf_capital\\common\\reports\\999_report.md\n"
    "- 커밋: abc123\n"
    "- 요약: 테스트용 보고서\n"
)


class ValidateReportTests(unittest.TestCase):
    def test_well_formed_report_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "999_report.md"
            path.write_text(GOOD_REPORT, encoding="utf-8")
            result = MODULE.validate_report(path)
        self.assertTrue(result.passed)
        self.assertEqual(result.missing_fields, [])
        self.assertEqual(result.status_value, "DONE")
        self.assertTrue(result.status_value_recognized)

    def test_missing_field_fails(self):
        text = GOOD_REPORT.replace("- 커밋: abc123\n", "")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "999_report.md"
            path.write_text(text, encoding="utf-8")
            result = MODULE.validate_report(path)
        self.assertFalse(result.passed)
        self.assertEqual(result.missing_fields, ["커밋"])

    def test_unrecognized_status_value_fails(self):
        text = GOOD_REPORT.replace("- 상태: DONE\n", "- 상태: MAYBE\n")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "999_report.md"
            path.write_text(text, encoding="utf-8")
            result = MODULE.validate_report(path)
        self.assertFalse(result.passed)
        self.assertEqual(result.missing_fields, [])
        self.assertFalse(result.status_value_recognized)

    def test_fail_and_partial_status_values_are_valid(self):
        for status in ("FAIL", "부분완료"):
            text = GOOD_REPORT.replace("- 상태: DONE\n", f"- 상태: {status}\n")
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "999_report.md"
                path.write_text(text, encoding="utf-8")
                result = MODULE.validate_report(path)
            self.assertTrue(result.passed, f"status {status} should be valid")

    def test_completely_empty_file_reports_all_fields_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "999_report.md"
            path.write_text("", encoding="utf-8")
            result = MODULE.validate_report(path)
        self.assertFalse(result.passed)
        self.assertEqual(set(result.missing_fields), set(MODULE.REQUIRED_FIELDS))


class FindReportPathTests(unittest.TestCase):
    def test_resolves_single_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            reports_dir = Path(tmp)
            (reports_dir / "999_smoke.md").write_text(GOOD_REPORT, encoding="utf-8")
            with unittest.mock.patch.object(MODULE, "REPORTS_DIR", reports_dir):
                found = MODULE.find_report_path("999")
        self.assertEqual(found.name, "999_smoke.md")

    def test_no_match_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            with unittest.mock.patch.object(MODULE, "REPORTS_DIR", Path(tmp)):
                self.assertIsNone(MODULE.find_report_path("999"))

    def test_ambiguous_match_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            reports_dir = Path(tmp)
            (reports_dir / "999_a.md").write_text(GOOD_REPORT, encoding="utf-8")
            (reports_dir / "999_b.md").write_text(GOOD_REPORT, encoding="utf-8")
            with unittest.mock.patch.object(MODULE, "REPORTS_DIR", reports_dir):
                self.assertIsNone(MODULE.find_report_path("999"))


class MainCliTests(unittest.TestCase):
    def test_main_returns_zero_for_passing_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "999_report.md"
            path.write_text(GOOD_REPORT, encoding="utf-8")
            self.assertEqual(MODULE.main(["--path", str(path)]), 0)

    def test_main_returns_two_for_missing_file(self):
        self.assertEqual(MODULE.main(["--path", r"C:\does\not\exist.md"]), 2)

    def test_main_returns_one_for_failing_report(self):
        text = GOOD_REPORT.replace("- 커밋: abc123\n", "")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "999_report.md"
            path.write_text(text, encoding="utf-8")
            self.assertEqual(MODULE.main(["--path", str(path)]), 1)


if __name__ == "__main__":
    unittest.main()
