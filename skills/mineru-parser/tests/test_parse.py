import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
if (ROOT / "mineru-parser" / "parse.py").exists():
    MODULE_PATH = ROOT / "mineru-parser" / "parse.py"
else:
    MODULE_PATH = ROOT / "parse.py"
SPEC = importlib.util.spec_from_file_location("mineru_parse", MODULE_PATH)
mineru_parse = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mineru_parse)


class ResolveApiTokenTests(unittest.TestCase):
    def test_environment_token_takes_precedence(self):
        config = {"api_token": "config-token"}
        with mock.patch.dict(os.environ, {"MINERU_TOKEN": "env-token"}, clear=False):
            self.assertEqual(mineru_parse.resolve_api_token(config), "env-token")

    def test_falls_back_to_config_token(self):
        config = {"api_token": "config-token"}
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(mineru_parse.resolve_api_token(config), "config-token")


class ResolveOutputDirTests(unittest.TestCase):
    def test_local_file_defaults_to_sibling_output_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "paper.pdf"
            source.write_text("x", encoding="utf-8")
            result = mineru_parse.resolve_output_dir(str(source), None, "~/unused")
            self.assertEqual(result.name, "paper_mineru_output")
            self.assertEqual(result.parent.resolve(), source.parent.resolve())

    def test_explicit_output_overrides_default(self):
        result = mineru_parse.resolve_output_dir(
            "https://example.com/doc.pdf",
            "~/custom-output",
            "~/fallback-output",
        )
        self.assertEqual(result, Path("~/custom-output").expanduser())


class UtilityTests(unittest.TestCase):
    def test_mask_secret_short_value(self):
        self.assertEqual(mineru_parse.mask_secret("abcd"), "****")

    def test_mask_secret_long_value(self):
        self.assertEqual(mineru_parse.mask_secret("abcdefgh1234"), "abcd...1234")


if __name__ == "__main__":
    unittest.main()
