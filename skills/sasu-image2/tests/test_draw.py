import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "draw.py"
SPEC = importlib.util.spec_from_file_location("sasu_draw", MODULE_PATH)
sasu_draw = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sasu_draw)


class ValidateSizeTests(unittest.TestCase):
    def test_accepts_supported_size(self):
        sasu_draw.validate_size("1024x1536")

    def test_rejects_unsupported_size(self):
        with self.assertRaises(SystemExit):
            sasu_draw.validate_size("999x999")


class ResolveOutputPathTests(unittest.TestCase):
    def test_rejects_directory_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(SystemExit):
                sasu_draw.resolve_output_path(temp_dir)

    def test_accepts_file_path(self):
        result = sasu_draw.resolve_output_path("outputs/imagegen/test.png")
        self.assertEqual(result, Path("outputs/imagegen/test.png"))


if __name__ == "__main__":
    unittest.main()
