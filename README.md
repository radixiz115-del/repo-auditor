# repo-auditor

[![CI](https://github.com/radixiz115-del/repo-auditor/actions/workflows/ci.yml/badge.svg)](https://github.com/radixiz115-del/repo-auditor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Быстрая проверка «гигиены» репозитория: README, лицензия, .gitignore, CI, тесты, секреты, большие файлы. Выдаёт оценку 0-100 и конкретные советы, что починить. Работает как CLI и как GitHub Action, который сам пишет отчёт комментарием в pull request.

Без внешних зависимостей, нужен только Python 3.9+.

## Installation

```bash
git clone https://github.com/radixiz115-del/repo-auditor
cd repo-auditor
```

## Usage

```bash
python repo_auditor.py .                    # проверить текущую папку
python repo_auditor.py ~/code/myproject     # проверить другой репозиторий
python repo_auditor.py . --format json      # машиночитаемый вывод
python repo_auditor.py . --format markdown  # отчёт в виде Markdown-таблицы
python repo_auditor.py . --fail-under 70    # код выхода 1, если оценка ниже 70
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

## Использование как GitHub Action

Добавь в свой репозиторий файл `.github/workflows/audit.yml`:

```yaml
name: Audit

on: pull_request

permissions:
  contents: read
  pull-requests: write

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: radixiz115-del/repo-auditor@v1
        with:
          fail-under: 70   # необязательно
```

В каждом pull request появится комментарий с оценкой и таблицей проверок. При новых коммитах комментарий обновляется, а не дублируется. Отчёт также попадает в Summary запуска.

| Параметр | По умолчанию | Описание |
|---|---|---|
| `path` | `.` | Какую папку проверять |
| `fail-under` | `0` | Упасть, если оценка ниже порога (0 = не падать) |
| `comment` | `true` | Писать комментарий в PR |
| `github-token` | `github.token` | Токен для комментария |

Output: `score` — оценка 0-100, её можно использовать в следующих шагах workflow.

Для PR из форков у токена нет прав на комментарий, в этом случае отчёт виден только в Summary запуска.

## Что проверяется

| Проверка | Вес | Что смотрит |
|---|---|---|
| README | 15 | Файл существует и содержит больше 300 символов |
| Разделы README | 5 | Есть установка и использование |
| Лицензия | 15 | LICENSE, LICENSE.md, LICENSE.txt или COPYING |
| CI | 15 | Есть workflow в `.github/workflows/` |
| Тесты | 15 | Файлы или папка с тестами |
| .gitignore | 10 | Файл существует |
| .env | 10 | В репозитории нет закоммиченного `.env` |
| Секреты | 10 | В коде нет ключей AWS, токенов GitHub и приватных ключей |
| Файлы для контрибьюторов | 5 | CONTRIBUTING, SECURITY или шаблоны issue/PR |
| Большие файлы | 5 | Нет файлов тяжелее 5 МБ |

Оценка равна доле набранных баллов от максимума.

## Roadmap

- [x] CLI с оценкой и подсказками
- [x] GitHub Action с комментарием в PR
- [ ] Конфиг `.repo-auditor.toml` (свои веса, отключение проверок)
- [ ] Проверка устаревших зависимостей
- [ ] Значок с оценкой для README

## Contributing

Pull request'ы приветствуются, подробности в [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
