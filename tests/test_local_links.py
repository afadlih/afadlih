from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_local_links.py"
spec = importlib.util.spec_from_file_location("validate_local_links", MODULE_PATH)
validate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate)


class LocalLinkValidationTests(unittest.TestCase):
    def test_fenced_diff_links_are_not_treated_as_document_links(self):
        text = """Before\n\n```diff\n+[Case study](case-studies/private/README.md)\n+<img src=\"assets/private.svg\" />\n```\n\n[Visible](../README.md)\n"""
        visible = validate.without_fenced_code(text)
        self.assertNotIn("case-studies/private/README.md", visible)
        self.assertNotIn("assets/private.svg", visible)
        self.assertIn("[Visible](../README.md)", visible)

    def test_tilde_fences_and_long_closing_markers_are_supported(self):
        text = """~~~markdown\n[Ignored](missing.md)\n~~~~\n[Kept](../README.md)\n"""
        visible = validate.without_fenced_code(text)
        self.assertNotIn("missing.md", visible)
        self.assertIn("../README.md", visible)


if __name__ == "__main__":
    unittest.main()
