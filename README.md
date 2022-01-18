# Описание.

Проект «Yatube» - социальная сеть для публикации дневников.Разработан по классической MVT архитектуре. Используется пагинация постов и кэширование. Регистрация реализована с верификацией данных, сменой и востановлением пароля через почту. Написаны тесты, проверяющие работу сервиса.
Стек: Python 3, Django 3, SQLite3, pytest

# Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/KaterinaSolovyeva/hw05_final

```
```
cd hw05_final
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
```
source env/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
