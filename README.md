# Random Password Generator

**Автор:** Плумаки Анна Янис

**GitHub:** https://github.com/plumakianna-prog/password-generator

## Описание программы

Random Password Generator — это графическое приложение (GUI) на Python с использованием библиотеки tkinter.  
Программа позволяет генерировать случайные пароли с настраиваемыми параметрами:

- длина пароля (от 4 до 64 символов)
- использование цифр
- использование букв (A-Z, a-z)
- использование спецсимволов (!@#$%^&*)

Все сгенерированные пароли сохраняются в историю (файл `password_history.json`) с указанием длины и даты создания.

## Требования для запуска

- Python 3.7 или выше
- Встроенные библиотеки: `tkinter`, `random`, `string`, `json`, `datetime` — дополнительной установки не требуют

## Как запустить

```bash
git clone https://github.com/plumakianna-prog/password-generator.git
cd password-generator
python password_generator.py
