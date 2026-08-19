# PoE Uniques Analytics API

Асинхронный REST API сервис для приема, агрегации и выдачи аналитики предметам (T0/T1) в реальном времени. Принимает JSON-пакеты от клиентского оверлея, объединяет данные на уровне СУБД и отдаёт готовые расчеты.
(также хранит данные о каждом предмете в бд)

## Стек

* **Фреймворк:** FastAPI (Python 3.11+)
* **Валидация и конфиг:** Pydantic v2, Pydantic-Settings
* **База данных:** PostgreSQL
* **ORM & Driver:** SQLAlchemy 2.0 (Async) + `asyncpg`
* **Деплой:** Docker, Docker Compose

---

## Деплой

Вся инфраструктура полностью контейнеризована (Сервер + PostgreSQL). 

### Настройка окружения (`.env`)
Создайте файл `.env` в корневой директории проекта со своими ключами доступа и параметрами БД:

```env
DATABASE_URL=postgresql+asyncpg://postgres_user:your_key@db:5432/analytics_db
API_KEY=your_key
```

### Запуск

docker compose up --build -d

апишка на http://localhost:8000
доки на http://localhost:8000/docs

