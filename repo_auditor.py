#!/usr/bin/env python3
"""repo-auditor: быстрая проверка «гигиены» репозитория."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}
MAX_FILE_MB = 5
SECRET_PATTERNS = {
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Private key": re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
}
TEXT_EXT = {".py", ".js", ".ts", ".json", ".yml", ".yaml", ".env", ".txt", ".md", ".cfg", ".ini", ".toml", ".sh"}


@dataclass
class Result:
    name: str
    passed: bool
    weight: int
    hint: str


def walk(root: Path):
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.is_file():
            yield p


def exists_any(root: Path, names: list[str]) -> bool:
    lower = {p.name.lower() for p in root.iterdir()}
    return any(n.lower() in lower for n in names)


def check_readme(root: Path) -> Result:
    for p in root.iterdir():
        if p.name.lower().startswith("readme") and p.is_file():
            text = p.read_text(errors="ignore")
            ok = len(text) > 300
            return Result("README достаточно подробный", ok, 15,
                          "Добавь описание, установку и пример использования (>300 символов).")
    return Result("README существует", False, 15, "Создай README.md с описанием проекта.")


def check_readme_sections(root: Path) -> Result:
    for p in root.iterdir():
        if p.name.lower().startswith("readme") and p.is_file():
            text = p.read_text(errors="ignore").lower()
            ok = any(w in text for w in ("install", "установ")) and any(w in text for w in ("usage", "использован", "пример"))
            return Result("README: установка и использование", ok, 5,
                          "Добавь разделы Installation и Usage.")
    return Result("README: установка и использование", False, 5, "Нет README.")


def check_license(root: Path) -> Result:
    ok = exists_any(root, ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"])
    return Result("Лицензия", ok, 15, "Без лицензии другие не могут легально использовать код. См. choosealicense.com.")


def check_gitignore(root: Path) -> Result:
    return Result(".gitignore", (root / ".gitignore").exists(), 10, "Добавь .gitignore (gitignore.io).")


def check_ci(root: Path) -> Result:
    wf = root / ".github" / "workflows"
    ok = wf.is_dir() and any(wf.glob("*.y*ml"))
    return Result("CI (GitHub Actions)", ok, 15, "Добавь workflow в .github/workflows/ с тестами/линтером.")


def check_tests(root: Path) -> Result:
    ok = any(
        p.name.startswith("test_") or p.name.endswith(("_test.py", ".test.js", ".test.ts", "_test.go", ".spec.ts", ".spec.js"))
        or "tests" in p.relative_to(root).parts or "test" in p.relative_to(root).parts
        for p in walk(root)
    )
    return Result("Тесты", ok, 15, "Добавь хотя бы базовые тесты.")


def check_community(root: Path) -> Result:
    ok = exists_any(root, ["CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md"]) or (root / ".github").is_dir() and any(
        (root / ".github" / n).exists() for n in ("CONTRIBUTING.md", "SECURITY.md", "ISSUE_TEMPLATE", "PULL_REQUEST_TEMPLATE.md"))
    return Result("Файлы для контрибьюторов", ok, 5, "Добавь CONTRIBUTING.md или шаблоны issue/PR.")


def check_big_files(root: Path) -> Result:
    big = [str(p.relative_to(root)) for p in walk(root) if p.stat().st_size > MAX_FILE_MB * 1024 * 1024]
    hint = "Большие файлы (>%d МБ): %s. Используй Git LFS или убери из репо." % (MAX_FILE_MB, ", ".join(big[:3]))
    return Result("Нет больших файлов", not big, 5, hint)


def check_env_files(root: Path) -> Result:
    bad = [str(p.relative_to(root)) for p in walk(root) if p.name == ".env"]
    return Result("Нет закоммиченного .env", not bad, 10, "Найден .env: %s. Удали и добавь в .gitignore." % ", ".join(bad))


def check_secrets(root: Path) -> Result:
    found = []
    for p in walk(root):
        if p.suffix.lower() not in TEXT_EXT or p.stat().st_size > 1_000_000:
            continue
        text = p.read_text(errors="ignore")
        for label, rx in SECRET_PATTERNS.items():
            if rx.search(text):
                found.append(f"{label} в {p.relative_to(root)}")
    return Result("Нет очевидных секретов в коде", not found, 20 if found else 10,
                  "Возможные секреты: %s. Отзови ключи и вычисти историю." % "; ".join(found[:3]))


CHECKS = [check_readme, check_readme_sections, check_license, check_gitignore, check_ci,
          check_tests, check_community, check_big_files, check_env_files, check_secrets]


def run(root: Path) -> tuple[int, list[Result]]:
    results = [c(root) for c in CHECKS]
    total = sum(r.weight for r in results)
    got = sum(r.weight for r in results if r.passed)
    return round(100 * got / total), results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Проверка гигиены репозитория")
    ap.add_argument("path", nargs="?", default=".", help="путь к репозиторию")
    ap.add_argument("--json", action="store_true", help="вывод в JSON")
    ap.add_argument("--fail-under", type=int, default=0, help="код выхода 1, если оценка ниже порога (для CI)")
    args = ap.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Не папка: {root}", file=sys.stderr)
        return 2

    score, results = run(root)
    if args.json:
        print(json.dumps({"score": score, "checks": [asdict(r) for r in results]}, ensure_ascii=False, indent=2))
    else:
        print(f"\nАудит: {root.name}\n" + "-" * 40)
        for r in results:
            print(f"  {'✓' if r.passed else '✗'} {r.name}")
            if not r.passed:
                print(f"      → {r.hint}")
        print("-" * 40 + f"\nОценка: {score}/100\n")
    return 1 if score < args.fail_under else 0


if __name__ == "__main__":
    sys.exit(main())
