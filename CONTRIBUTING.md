# Contributing

Спасибо за интерес к проекту!

1. Сделай fork и создай ветку: `git checkout -b my-feature`
2. Внеси изменения и добавь тест в `tests/`
3. Проверь локально: `python -m unittest discover -s tests`
4. Открой Pull Request с кратким описанием, что и зачем изменено

Новые проверки добавляются функцией `check_...` в `repo_auditor.py` и регистрируются в списке `CHECKS`.
