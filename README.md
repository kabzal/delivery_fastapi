# Задание: разработка API для курьерской компании

Данный проект представляет собой сервис для автоматизированного получения заказов от крупных и постоянных клиентов курьерской компании. Реализация на FastAPI, 
в качестве базы данных используется PostgreSQL, для работы с БД используются SQLAlchemy, Alembic.

**Примечание: решение задания по SQL-запросам находится в файле `sql_tasks_answers.md`**

## Функционал сервиса
Данный сервис поддерживает следующйи функционал:
- создание новой заявки на доставку (одновременно ей присваивается статус `new`)
- получение данных о заявке по `internal_id`
- обновление заявки по ее `internal_id`
- получение статуса заявки по ее `internal_id`
- обновление статуса заявки по ее `internal_id`

## Установка
1. Клонируйте репозиторий:
```bash
git clone https://github.com/kabzal/delivery_fastapi.git
cd delivery_fastapi
```
2. Установите зависимости проекта:
```bash
pip install -r requirements.txt
```
3. Добавьте в проект файл `.env`, содержащий переменные по примеру `.env.example`:
- `DB_USER` - имя пользователя БД;
- `DB_PASS` - пароль пользователя БД;
- `DB_HOST` - хост, например `localhost`;
- `DB_PORT` - порт, например `5432`;
- `DB_NAME` - имя БД;
- `DADATA_TOKEN` - токен от сервиса Dadata для корректировки адресов;
- `DADATA_SECRET` - секретный ключ от сервиса Dadata для корректировки адресов.
4. Настройте БД PostgreSQL так, чтобы в ней были соответствующие `.env` параметры.
5. Примените миграции `alembic`:
```bash
alembic upgrade head
```
6. Запустите сервис:
```bash
uvicorn main:app --reload
```

## Использование сервиса
После запуска сервер будет доступен по адресу `http://127.0.0.1:8000`. Рекомендуется тестировать функционал через `http://127.0.0.1:8000/docs`.

### API Эндпоинты
1. GET /request/{internal_id}/
- Описание: Получение информации о заявке по internal_id.
- Пример ответа:
```python
{
  "delivery_city": "Казань", # Город доставки
  "delivery_address": "г Казань, ул Патриса Лумумбы, д 11", # Адрес доставки
  "delivery_date": "2024-09-13", # Дата доставки
  "delivery_time": "12:00:00", # Время доставки
  "customer_name": "Иван Иванов", # Имя клиента
  "comment": "Оставить у двери", # Комментарий
  "package_type": "Бандероль",  # Тип посылки. Габаритный груз доступен только в Казани
  "internal_id": 27,  # внутренний id заявки
  "load_date": "2024-09-13T00:00:00",  # Время создания заявки
  "distance": 3.387563097970843  # Расстояние от склада в км
}
```
2. PUT /request/{internal_id}/
- Описание: Обновление информации о заявке по internal_id.
- Необходимо отправить данные в следующем формате:
```python
{
  "delivery_city": "Казань",
  "delivery_address": "г Казань, ул Патриса Лумумбы, д 12",
  "delivery_date": "2024-09-14",
  "delivery_time": "12:00:00",
  "customer_name": "Иван Иванов",
  "comment": "Вручить в руки",  # Необязательный параметр, можно пропустить, тогда комментария не будет
  "package_type": "Письмо"
}
```
- В случае успешного обновления вернется сообщение об успехе.
3. POST /request/
- Описание: Создание новой заявки.
- Необходимо отправить данные в следующем формате:
```python
{
  "delivery_city": "Казань",
  "delivery_address": "г Казань, ул Патриса Лумумбы, д 12",
  "delivery_date": "2024-09-14",
  "delivery_time": "12:00:00",
  "customer_name": "Иван Иванов",
  "comment": "Вручить в руки",  # Необязательный параметр, можно пропустить, тогда комментария не будет
  "package_type": "Письмо"  # Габаритный груз доступен только в Казани
}
```
- В случае успешного создания вернется internal_id созданной заявки.
- Одновременно с созданием заявки ей будет присвоен статус `new`.
4. GET /request/{internal_id}/status/
- Описание: Получение информации о текущем статусе заявки по internal_id.
- Пример ответа:
```python
{
  "internal_id": 27,  # внутренний id заявки
  "status_name": "new",  # текущий статус
  "load_date": "2024-09-13T00:00:00"   # Дата и время установки данного статуса
}
```
5. PUT /request/{internal_id}/status/
- Описание: Обновление информации о текущем статусе заявки по internal_id.
- Необходимо отправить данные об internal_id (как Path-параметр) и новом статусе по примеру:
```python
{
  "new_status": "done"
}
```
- В случае успешного обновления статуса вернется сообщение об успехе.

### Валидации
При внесении данных есть следующие валидации:
1. Для типов посылок `packagetype` доступны значения `Письмо`, `Бандероль` и `Габаритный груз`.
2. Тип посылки `Габаритный груз` доступен только в городе `Казань`.
3. Доступные города доставки `delivery_city`: `Казань`, `Набережные Челны`, `Нижнекамск`, `Альметьевск`, `Зеленодольск`.
4. Доступные статусы заявок: `new`, `in progress`, `handed to courier`, `done`, `cancelled`.
5. Адрес доставки `delivery_address` валидируется и корректируется с помощью сервиса Dadata. Если адрес не найден, необходимо проверить его написание.
