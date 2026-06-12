import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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


class RuntimeDefaultsTests(unittest.TestCase):
    def test_uses_school_base_url_by_default(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(sasu_draw, "load_local_config", return_value={}):
                result = sasu_draw.load_runtime_defaults()
        self.assertEqual(result["base_url"], "http://10.15.46.72:8010/v1")

    def test_env_base_url_overrides_default(self):
        with mock.patch.dict(
            os.environ,
            {"SASU_IMAGE2_BASE_URL": "http://127.0.0.1:9000/v1"},
            clear=True,
        ):
            with mock.patch.object(sasu_draw, "load_local_config", return_value={}):
                result = sasu_draw.load_runtime_defaults()
        self.assertEqual(result["base_url"], "http://127.0.0.1:9000/v1")


if __name__ == "__main__":
    unittest.main()
