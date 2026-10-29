import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import repo_auditor as ra  # noqa: E402


def make_repo(files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp())
    for name, content in files.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    return root


class AuditorTests(unittest.TestCase):
    def test_empty_repo_scores_low(self):
        score, _ = ra.run(make_repo({"x.txt": "hi"}))
        self.assertLess(score, 40)

    def test_good_repo_scores_high(self):
        readme = "# Demo\n## Installation\npip install\n## Usage\nrun it\n" + "text " * 80
        root = make_repo({
            "README.md": readme,
            "LICENSE": "MIT",
            ".gitignore": "__pycache__/",
            ".github/workflows/ci.yml": "name: ci",
            "tests/test_a.py": "",
            "CONTRIBUTING.md": "hi",
        })
        score, _ = ra.run(root)
        self.assertEqual(score, 100)

    def test_detects_aws_key(self):
        fake_key = "AKIA" + "ABCDEFGHIJKLMNOP"  # собираем по частям, чтобы не светить в исходнике
        root = make_repo({"config.py": f'KEY = "{fake_key}"'})
        self.assertFalse(ra.check_secrets(root).passed)

    def test_detects_env_file(self):
        root = make_repo({".env": "SECRET=1"})
        self.assertFalse(ra.check_env_files(root).passed)

    def test_license_detected(self):
        self.assertTrue(ra.check_license(make_repo({"LICENSE": "x"})).passed)

    def test_fail_under_exit_code(self):
        root = make_repo({"x.txt": "hi"})
        self.assertEqual(ra.main([str(root), "--fail-under", "90"]), 1)
        self.assertEqual(ra.main([str(root)]), 0)

    def test_markdown_report(self):
        root = make_repo({"x.txt": "hi"})
        score, results = ra.run(root)
        md = ra.to_markdown("demo", score, results)
        self.assertIn(ra.MARKER, md)
        self.assertIn(f"{score}/100", md)
        self.assertIn("❌", md)

    def test_github_output(self):
        import os
        out = Path(tempfile.mkdtemp()) / "out.txt"
        os.environ["GITHUB_OUTPUT"] = str(out)
        try:
            ra.main([str(make_repo({"x.txt": "hi"})), "--format", "markdown", "--github-output"])
        finally:
            del os.environ["GITHUB_OUTPUT"]
        self.assertRegex(out.read_text(), r"score=\d+")


if __name__ == "__main__":
    unittest.main()
