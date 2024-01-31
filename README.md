## Проект «Blogicum»  
***
### Описание:
Проект «Blogicum» - это cоциальная сеть с авторизацией для добавления постов, комментариев.
***
### Системные требования:
Python 3.9 или выше.
***
### Установка:

1. Склонируйте репозиторий по ссылке:
```
git clone git@github.com:Freelancerroma/django_sprint4.git
```
2. Установите и активируйте виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
3. Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
4. Перейдите в директорию blogicum и выполните миграции:
```
python manage.py makemigrations
```
```
python manage.py migrate
```
5. Выполните команду для загрузки фикстур в БД:
```
python manage.py loaddata db.json
```
6. Запустите локальный сервер:
```
python manage.py runserver
```
6. Перейдите по адресу локального сервера:
```
http://127.0.0.1:8000/
```
***
### Инструменты и стек:
- Python
- HTML
- CSS
- Django
- Bootstrap
- Pytest
