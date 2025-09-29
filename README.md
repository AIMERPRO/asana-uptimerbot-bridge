# Asana → UptimeRobot Bridge

Микросервис на **FastAPI**, который принимает запросы (при выполнении скрипта) из Asana при перемещении задач и автоматически создаёт HTTP-мониторы в [UptimeRobot](https://uptimerobot.com).

---

## 🚀 Возможности

* Принимает POST-запросы из Asana (`/asana-webhook/{ASANA_PATH_TOKEN}`).
* Извлекает домен из задачи (кастомное поле).
* Проверяет, есть ли уже монитор для этого домена.
* Создаёт новый HTTP-монитор.

---

## ⚙️ Конфигурация

Все настройки берутся из переменных окружения (`.env`):

```env
# токен UptimeRobot API v3
UPTIMEROBOT_API_KEY=TOP_SECRET

# схема для мониторов (https или http)
DEFAULT_SCHEME=https

# токен пути Asana (секрет в URL)
ASANA_PATH_TOKEN=TOP_SECRET

# количество воркеров Uvicorn
UVICORN_WORKERS=4
```

---

## 🔌 API

# API Swager 
URL - `/docs`

### POST `/asana-webhook/{token}`

**Headers:**
`Content-Type: application/json`

**Body (пример из Asana):**

```json
{
  "taskGid": "1211476405634439",
  "custom_fields": [
    {
      "gid": "1211475093285235",
      "name": "Домен",
      "display_value": "https://test-domain.com",
      "text_value": "https://test-domain.com",
      "type": "text"
    }
  ],
  "name": "Test Task"
}
```

**Response:**

```json
{
  "ok": true,
  "created": {
    "id": "801430564",
    "url": "https://test-domain.com",
    "status": "success"
  }
}
```

Ошибки возвращаются в формате:

```json
{ "ok": false, "error": "domain_not_found" }
```

---

## 🧩 Структура проекта

```
app/
 ├── main.py            # FastAPI приложение
 ├── uptime_robot.py    # клиент для API UptimeRobot
 ├── utils.py           # вспомогательные функции
 ├── config.py          # конфигурация из env
.env                    # .env конфиг
.docker-compose.yml     # Docker-compose файл
Dockerfile              # Настройка Docker
README.md               # Вы здесь
requirements.txt        # Зависимости
```

---

## 🛠️ Разработка

Установить зависимости:

```bash
pip install -r requirements.txt
```

Запуск локально:

```bash
uvicorn app.main:app --reload --port 8000
```

Тест вебхука:

```bash
curl -X POST http://localhost:8000/asana-webhook/<ASANA_PATH_TOKEN> \
     -H "Content-Type: application/json" \
     -d '{"taskGid":"1","custom_fields":[{"name":"Домен","text_value":"https://example.com"}]}'
```

---
