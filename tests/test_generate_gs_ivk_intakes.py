import json
import tempfile
import unittest
from pathlib import Path

from scripts.generate_gs_ivk_intakes import write_intakes


class GenerateGsIvkIntakesTests(unittest.TestCase):
    def test_generates_contract_and_refuses_changed_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "idx.csv"
            source.write_text(
                '"group","symbol","weight"\n'
                '"optic_idx","LITE",50\n'
                '"optic_idx","COHR",50\n',
                encoding="utf-8",
            )
            output = root / "intakes"
            files = write_intakes(
                market="us", sheet="us_idx", csv_path=source, output_dir=output
            )
            self.assertEqual([output / "us_optic.json"], files)
            intake = json.loads(files[0].read_text(encoding="utf-8"))
            self.assertEqual("ivk-intake-1.0", intake["contract_version"])
            self.assertEqual("new", intake["operation"])
            self.assertEqual(["LITE", "COHR"], intake["seed"])
            self.assertEqual("matrix", intake["frame"])
            self.assertEqual("approval_required", intake["options"]["write_policy"])

            files[0].write_text("{}\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                write_intakes(
                    market="us", sheet="us_idx", csv_path=source, output_dir=output
                )


if __name__ == "__main__":
    unittest.main()
