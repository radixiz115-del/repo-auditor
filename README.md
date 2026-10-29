[![CI](https://github.com/radixiz115-del/repo-auditor/actions/workflows/ci.yml/badge.svg)](https://github.com/radixiz115-del/repo-auditor/actions/workflows/ci.yml)
# repo-auditor

Быстрая проверка «гигиены» репозитория: README, лицензия, .gitignore, CI, тесты, секреты, большие файлы. Выдаёт оценку 0–100 и конкретные советы, что починить.

Без внешних зависимостей, нужен только Python 3.9+.

## Installation

```bash
git clone https://github.com/<you>/repo-auditor
cd repo-auditor
```

## Usage

```bash
python repo_auditor.py .                  # проверить текущую папку
python repo_auditor.py ~/code/myproject   # проверить другой репозиторий
python repo_auditor.py . --json           # машиночитаемый вывод
python repo_auditor.py . --fail-under 70  # упасть в CI, если оценка < 70
```

Пример вывода:

```
Аудит: myproject
----------------------------------------
  ✓ README достаточно подробный
  ✗ Лицензия
      → Без лицензии другие не могут легально использовать код.
----------------------------------------
Оценка: 85/100
```

## Что проверяется

README (наличие, длина, разделы), LICENSE, .gitignore, GitHub Actions, тесты, CONTRIBUTING/SECURITY/шаблоны, файлы >5 МБ, закоммиченный `.env`, типовые секреты (AWS, GitHub-токены, приватные ключи).

## Roadmap

- [ ] Оформить как GitHub Action с комментарием в PR
- [ ] Проверка устаревших зависимостей
- [ ] Конфиг `.repo-auditor.toml` (веса, отключение проверок)
- [ ] Значок с оценкой для README

## License

MIT
