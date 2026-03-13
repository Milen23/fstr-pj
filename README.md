# FSTR API

REST API для Федерации спортивного туризма России (ФСТР). Сервис позволяет туристам добавлять информацию о перевалах, редактировать её и отслеживать статус модерации.

## О проекте

Проект разработан в рамках учебного задания. API позволяет мобильному приложению взаимодействовать с базой данных перевалов. Турист может отправить фотографии и описание перевала, а сотрудники ФСТР проводят модерацию, меняя статус объекта.

## Технологии

- Python 3.9+
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Marshmallow (валидация данных)

## Структура базы данных

База данных состоит из следующих таблиц:
- users - информация о пользователях
- coords - координаты перевалов
- perevals - основная информация о перевалах
- images - фотографии перевалов
- difficulties - категории сложности по сезонам

Статусы перевалов:
- new - добавлен, ожидает модерации
- pending - взят в работу модератором
- accepted - модерация пройдена успешно
- rejected - информация не принята

## Установка и запуск

1. Клонировать репозиторий:
   git clone https://github.com/ваш-логин/fstr-api.git
   cd fstr-api

2. Создать виртуальное окружение:
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate     # для Windows

3. Установить зависимости:
   pip install -r requirements.txt

4. Создать базу данных PostgreSQL:
   sudo -u postgres psql
   CREATE DATABASE fstr_db;
   CREATE USER fstr_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE fstr_db TO fstr_user;
   \q

5. Создать файл .env в корне проекта:
   FSTR_DB_HOST=localhost
   FSTR_DB_PORT=5432
   FSTR_DB_LOGIN=fstr_user
   FSTR_DB_PASS=your_password
   FSTR_DB_NAME=fstr_db

6. Инициализировать базу данных:
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade

7. Запустить сервер:
   python run.py

Сервер будет доступен по адресу: http://localhost:5000

## API Endpoints

### 1. Добавление нового перевала
POST /api/submitData

Добавляет информацию о новом перевале. При создании статус устанавливается в "new".

Обязательные поля:
- title - название перевала
- add_time - дата и время в формате "YYYY-MM-DD HH:MM:SS"
- user (объект с email, fam, name, phone)
- coords (объект с latitude, longitude, height)
- level (объект с полями по сезонам)
- images (массив объектов с data и title)

Пример запроса:
{
  "beauty_title": "пер. ",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2021-09-22 13:18:13",
  "user": {
    "email": "qwerty@mail.ru",
    "fam": "Пупкин",
    "name": "Василий",
    "otc": "Иванович",
    "phone": "+7 555 55 55"
  },
  "coords": {
    "latitude": 45.3842,
    "longitude": 7.1525,
    "height": 1200
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },
  "images": [
    {"data": "base64_encoded_image_1", "title": "Седловина"},
    {"data": "base64_encoded_image_2", "title": "Подъём"}
  ]
}

Успешный ответ (200):
{
  "status": 200,
  "message": "Отправлено успешно",
  "id": 42
}

Ошибка валидации (400):
{
  "status": 400,
  "message": "Bad Request: {'title': ['Missing data for required field.']}",
  "id": null
}

Ошибка сервера (500):
{
  "status": 500,
  "message": "Ошибка подключения к базе данных",
  "id": null
}

### 2. Получение перевала по ID
GET /api/submitData/<id>

Возвращает полную информацию о перевале, включая статус модерации.

Параметры:
- id - идентификатор перевала (целое число)

Пример запроса:
GET /api/submitData/42

Успешный ответ (200):
{
  "status": 200,
  "message": "ok",
  "pereval": {
    "id": 42,
    "beauty_title": "пер. ",
    "title": "Пхия",
    "other_titles": "Триев",
    "connect": "",
    "add_time": "2021-09-22 13:18:13",
    "status": "new",
    "user": {
      "email": "qwerty@mail.ru",
      "fam": "Пупкин",
      "name": "Василий",
      "otc": "Иванович",
      "phone": "+7 555 55 55"
    },
    "coords": {
      "latitude": 45.3842,
      "longitude": 7.1525,
      "height": 1200
    },
    "level": {
      "winter": "",
      "summer": "1А",
      "autumn": "1А",
      "spring": ""
    },
    "images": [
      {"data": "base64_encoded_image_1", "title": "Седловина"},
      {"data": "base64_encoded_image_2", "title": "Подъём"}
    ]
  }
}

Если перевал не найден (404):
{
  "status": 404,
  "message": "Pereval with id 42 not found",
  "pereval": null
}

### 3. Редактирование перевала
PATCH /api/submitData/<id>

Редактирует существующий перевал. Редактирование возможно ТОЛЬКО если статус перевала "new".
Нельзя редактировать данные пользователя (ФИО, email, телефон).

Параметры:
- id - идентификатор перевала (целое число)

Можно передавать любые поля из объекта перевала, кроме user:
- beauty_title
- title
- other_titles
- connect
- add_time
- coords (полностью или частично)
- level (полностью или частично)
- images (полностью заменяет список)

Пример запроса (обновление только названия и высоты):
PATCH /api/submitData/42
{
  "title": "Новое название перевала",
  "coords": {
    "height": 1350
  }
}

Успешный ответ (200):
{
  "state": 1,
  "message": "Pereval updated successfully"
}

Ошибка - нельзя редактировать (400):
{
  "state": 0,
  "message": "Cannot update pereval with status 'accepted'. Only 'new' status can be edited"
}

Ошибка - попытка редактировать пользователя (400):
{
  "state": 0,
  "message": "Cannot update user information (name, email, phone)"
}

Перевал не найден (404):
{
  "state": 0,
  "message": "Pereval with id 42 not found"
}

### 4. Список перевалов пользователя
GET /api/submitData/?user__email=<email>

Возвращает список всех перевалов, отправленных пользователем с указанным email.

Параметры запроса:
- user__email - email пользователя (обязательный)

Пример запроса:
GET /api/submitData/?user__email=qwerty@mail.ru

Успешный ответ (200):
{
  "status": 200,
  "message": "ok",
  "perevals": [
    {
      "id": 42,
      "beauty_title": "пер. ",
      "title": "Пхия",
      "other_titles": "Триев",
      "connect": "",
      "add_time": "2021-09-22 13:18:13",
      "status": "new",
      "coords": {
        "latitude": 45.3842,
        "longitude": 7.1525,
        "height": 1200
      },
      "level": {
        "winter": "",
        "summer": "1А",
        "autumn": "1А",
        "spring": ""
      },
      "images_count": 2
    },
    {
      "id": 43,
      "beauty_title": "пер. ",
      "title": "Другой перевал",
      "other_titles": "",
      "connect": "",
      "add_time": "2021-10-05 09:30:00",
      "status": "accepted",
      "coords": {
        "latitude": 46.1234,
        "longitude": 8.5678,
        "height": 1500
      },
      "level": {
        "winter": "1Б",
        "summer": "1А",
        "autumn": "1А",
        "spring": "1Б"
      },
      "images_count": 3
    }
  ]
}

Пользователь не найден (404):
{
  "status": 404,
  "message": "User with email qwerty@mail.ru not found",
  "perevals": []
}

## Примеры использования с curl

1. Добавление перевала:
   curl -X POST http://localhost:5000/api/submitData \
     -H "Content-Type: application/json" \
     -d '{"title":"Тестовый перевал","add_time":"2024-01-01 12:00:00","user":{"email":"test@mail.ru","fam":"Иванов","name":"Иван","phone":"+7 123 456 78 90"},"coords":{"latitude":45.0,"longitude":8.0,"height":1000},"level":{"summer":"1А"},"images":[{"data":"base64data","title":"Фото"}]}'

2. Получение перевала:
   curl http://localhost:5000/api/submitData/42

3. Редактирование перевала:
   curl -X PATCH http://localhost:5000/api/submitData/42 \
     -H "Content-Type: application/json" \
     -d '{"title":"Обновленное название"}'

4. Получение списка перевалов пользователя:
   curl "http://localhost:5000/api/submitData/?user__email=test@mail.ru"

## Статусы ответов API

- 200 OK - запрос выполнен успешно
- 400 Bad Request - ошибка в запросе (невалидные данные, отсутствуют обязательные поля)
- 404 Not Found - ресурс не найден
- 500 Internal Server Error - внутренняя ошибка сервера

## Особенности реализации

1. Все подключения к базе данных выполняются через переменные окружения
2. Валидация входящих данных выполняется с помощью Marshmallow схем
3. Транзакционность - при ошибке все изменения откатываются
4. Логирование всех операций и ошибок
5. При добавлении нового перевала автоматически устанавливается статус "new"
6. Редактирование доступно только для перевалов со статусом "new"
7. Данные пользователя защищены от изменений через PATCH запросы

## Требования к окружению

Переменные окружения (файл .env):
- FSTR_DB_HOST - хост базы данных
- FSTR_DB_PORT - порт базы данных
- FSTR_DB_LOGIN - логин для подключения к БД
- FSTR_DB_PASS - пароль для подключения к БД
- FSTR_DB_NAME - имя базы данных
