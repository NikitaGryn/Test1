# Центральный реестр (Система Б) — REST API

## Описание проекта

Проект представляет собой **REST API, эмулирующее работу Системы Б (центральный реестр)** в сценарии обмена юридически значимыми документами между двумя информационными системами:

- **Система А (внешняя)** — инициирует запросы и отправляет документы.
- **Система Б (центральный реестр)** — хранит документы и обеспечивает их целостность.

Все документы подписываются электронной цифровой подписью (ЭЦП). Хранение реализовано в памяти (при необходимости можно заменить на БД или блокчейн-подобную структуру).

### Основные возможности

- **Проверка доступности**: эндпоинт `/api/health`.
- **Получение исходящих сообщений**: Система А запрашивает список сообщений, направленных ей за период (с пагинацией). Тело запроса и ответа — подписанные данные (`SignedApiData`).
- **Приём входящих сообщений**: Система А отправляет пакет транзакций; реестр проверяет хэш транзакций, сохраняет их и при наличии `BankGuaranteeHash` в полезной нагрузке возвращает квитанции типа 215.

Формат обмена: полезная нагрузка в поле `Data` (Base64), подпись в `Sign`, сертификат отправителя в `SignerCert`.

---

## Установка и запуск

### Требования

- Python 3.10+
- pip

### Установка зависимостей

```bash
# Переход в каталог проекта
cd d:\Test1

# Создание виртуального окружения (рекомендуется)
python -m venv .venv

# Активация виртуального окружения
# Windows (cmd):
.venv\Scripts\activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### Запуск сервера

```bash
# Из корня проекта (где находится app.py и main.py)
python main.py
```

Сервер будет доступен по адресу: **http://127.0.0.1:8000**

- Документация Swagger UI: http://127.0.0.1:8000/docs  
- ReDoc: http://127.0.0.1:8000/redoc  

---

## Примеры curl-запросов для всех эндпоинтов

Базовый URL: `http://127.0.0.1:8000`. Все POST-запросы к API используют тип контента `application/json`.

### 1. Проверка доступности (Health Check)

```bash
curl -X GET "http://127.0.0.1:8000/api/health"
curl -X GET "https://est1-nikitagryn6043-lhk5p78z.leapcell.dev/api/health"
```

Ожидаемый ответ: `OK` (текст).

---

### 2. Получение исходящих сообщений (POST /api/messages/outgoing)

Запрос от имени Системы А: в теле передаётся подписанный объект `SignedApiData`, в котором в `Data` (Base64) закодирован JSON с полями `StartDate`, `EndDate`, `Limit`, `Offset`.

**Пример корректного запроса:**

```bash
curl -X POST "http://127.0.0.1:8000/api/messages/outgoing" ^
  -H "Content-Type: application/json" ^
  -d "{\"Data\":\"eyJTdGFydERhdGUiOiIyMDI1LTEyLTMxVDIxOjAwOjAwWiIsIkVuZERhdGUiOiIyMDI2LTEyLTMxVDIwOjU5OjAwWiIsIkxpbWl0IjoxMCwiT2Zmc2V0IjowfQ==\",\"Sign\":\"U1lTVEVNX0FfU0VBUkNI\",\"SignerCert\":\"U1lTVEVNX0E=\"}"
curl -X POST "https://est1-nikitagryn6043-lhk5p78z.leapcell.dev/api/messages/outgoing" ^
  -H "Content-Type: application/json" ^
  -d "{\"Data\":\"eyJTdGFydERhdGUiOiIyMDI1LTEyLTMxVDIxOjAwOjAwWiIsIkVuZERhdGUiOiIyMDI2LTEyLTMxVDIwOjU5OjAwWiIsIkxpbWl0IjoxMCwiT2Zmc2V0IjowfQ==\",\"Sign\":\"U1lTVEVNX0FfU0VBUkNI\",\"SignerCert\":\"U1lTVEVNX0E=\"}"
```

Для Linux/macOS (один строковый аргумент без `^`):

```bash
curl -X POST "http://127.0.0.1:8000/api/messages/outgoing" \
  -H "Content-Type: application/json" \
  -d '{"Data":"eyJTdGFydERhdGUiOiIyMDI1LTEyLTMxVDIxOjAwOjAwWiIsIkVuZERhdGUiOiIyMDI2LTEyLTMxVDIwOjU5OjAwWiIsIkxpbWl0IjoxMCwiT2Zmc2V0IjowfQ==","Sign":"U1lTVEVNX0FfU0VBUkNI","SignerCert":"U1lTVEVNX0E="}'
curl -X POST "https://est1-nikitagryn6043-lhk5p78z.leapcell.dev/api/messages/outgoing" \
  -H "Content-Type: application/json" \
  -d '{"Data":"eyJTdGFydERhdGUiOiIyMDI1LTEyLTMxVDIxOjAwOjAwWiIsIkVuZERhdGUiOiIyMDI2LTEyLTMxVDIwOjU5OjAwWiIsIkxpbWl0IjoxMCwiT2Zmc2V0IjowfQ==","Sign":"U1lTVEVNX0FfU0VBUkNI","SignerCert":"U1lTVEVNX0E="}'
```

Ответ — объект `SignedApiData` от Системы Б с списком транзакций (исходящих в SYSTEM_A) за указанный период.

---

### 3. Приём входящих сообщений (POST /api/messages/incoming)

Система А отправляет пакет транзакций в подписанном виде. В `Data` (Base64) — JSON с полями `Transactions` (массив транзакций) и `Count`.

**Пример корректного запроса:**

```bash
curl -X POST "http://127.0.0.1:8000/api/messages/incoming" ^
  -H "Content-Type: application/json" ^
  -d "{\"Data\":\"eyJUcmFuc2FjdGlvbnMiOlt7IlRyYW5zYWN0aW9uVHlwZSI6OSwiRGF0YSI6ImV5SkVZWFJoSWpvaVpYbEtUMWxYTVd4SmFtOXBNRW8zVVc1MFEyVkpSbmRwTUVvdlVYWjBRemN3V1ZCU2FEbERkekJaVEZGMFpFTTNNRmwzWnpCTVVGRnpUa2RCTUV4RVVYWmtSME13VEdwUmRVWjNhVWxwZDJsUmJVWjFZVEJrTVZsWVNtaGlibEpzV2xWb2FHTXlaMmxQYVVreFVrUmFSMDlGVlhsUlZFWkVUVEJKTlZKcVVrVk9NRlUwVVZSS1JFNVZTWGhTUkU1SFRtdFZORkZVYkVSTmExRXdVbXBhUWs5RlNYaFJlazVHVGxWWk0xRlViRVZOYTBrd1VYcGFSazlGV1hkUlZFVnBURU5LVkdGWFpIVkphbTlwVld0Vk5WSkdaM2hVYTNCVFRVUlJPVWxwZDJsVk1teHVZbTFXZVZFeVZubGtRMGsyU1d4S1JrOVZVbGxOUlRWSFZsZDRVbEJUU2praUxDSlRaVzVrWlhKQ2NtRnVZMmdpT2lKVFdWTlVSVTFmUVNJc0lsSmxZMlZwZG1WeVFuSmhibU5vSWpvaVUxbFRWRVZOWDBJaUxDSkpibVp2VFdWemMyRm5aVlI1Y0dVaU9qSXdNaXdpVFdWemMyRm5aVlJwYldVaU9pSXlNREkyTFRBekxUQTRWREV5T2pNMk9qTTNMalkyT1ZvaUxDSkRhR0ZwYmtkMWFXUWlPaUk1TmpRNU5ERTBNUzB3WVRJMkxUUmpOekl0T1RGa05TMHdZelJrWVRkaU1URXdOR1VpTENKUWNtVjJhVzkxYzFSeVlXNXpZV04wYVc5dVNHRnphQ0k2Ym5Wc2JDd2lUV1YwWVdSaGRHRWlPbTUxYkd4OSIsIkhhc2giOiIiLCJTaWduIjoiIiwiU2lnbmVyQ2VydCI6IlUxbFRWRVZOWDBFPSIsIlRyYW5zYWN0aW9uVGltZSI6IjIwMjYtMDMtMDhUMTI6MzY6MzcuNjcwWiIsIk1ldGFkYXRhIjpudWxsLCJUcmFuc2FjdGlvbkluIjpudWxsLCJUcmFuc2FjdGlvbk91dCI6bnVsbH1dLCJDb3VudCI6MX0=\",\"Sign\":\"U1lTVEVNX0FfSU5DT01JTkc=\",\"SignerCert\":\"U1lTVEVNX0E=\"}"
curl -X POST "https://est1-nikitagryn6043-lhk5p78z.leapcell.dev/api/messages/incoming" ^
  -H "Content-Type: application/json" ^
  -d "{\"Data\":\"eyJUcmFuc2FjdGlvbnMiOlt7IlRyYW5zYWN0aW9uVHlwZSI6OSwiRGF0YSI6ImV5SkVZWFJoSWpvaVpYbEtUMWxYTVd4SmFtOXBNRW8zVVc1MFEyVkpSbmRwTUVvdlVYWjBRemN3V1ZCU2FEbERkekJaVEZGMFpFTTNNRmwzWnpCTVVGRnpUa2RCTUV4RVVYWmtSME13VEdwUmRVWjNhVWxwZDJsUmJVWjFZVEJrTVZsWVNtaGlibEpzV2xWb2FHTXlaMmxQYVVreFVrUmFSMDlGVlhsUlZFWkVUVEJKTlZKcVVrVk9NRlUwVVZSS1JFNVZTWGhTUkU1SFRtdFZORkZVYkVSTmExRXdVbXBhUWs5RlNYaFJlazVHVGxWWk0xRlViRVZOYTBrd1VYcGFSazlGV1hkUlZFVnBURU5LVkdGWFpIVkphbTlwVld0Vk5WSkdaM2hVYTNCVFRVUlJPVWxwZDJsVk1teHVZbTFXZVZFeVZubGtRMGsyU1d4S1JrOVZVbGxOUlRWSFZsZDRVbEJUU2praUxDSlRaVzVrWlhKQ2NtRnVZMmdpT2lKVFdWTlVSVTFmUVNJc0lsSmxZMlZwZG1WeVFuSmhibU5vSWpvaVUxbFRWRVZOWDBJaUxDSkpibVp2VFdWemMyRm5aVlI1Y0dVaU9qSXdNaXdpVFdWemMyRm5aVlJwYldVaU9pSXlNREkyTFRBekxUQTRWREV5T2pNMk9qTTNMalkyT1ZvaUxDSkRhR0ZwYmtkMWFXUWlPaUk1TmpRNU5ERTBNUzB3WVRJMkxUUmpOekl0T1RGa05TMHdZelJrWVRkaU1URXdOR1VpTENKUWNtVjJhVzkxYzFSeVlXNXpZV04wYVc5dVNHRnphQ0k2Ym5Wc2JDd2lUV1YwWVdSaGRHRWlPbTUxYkd4OSIsIkhhc2giOiIiLCJTaWduIjoiIiwiU2lnbmVyQ2VydCI6IlUxbFRWRVZOWDBFPSIsIlRyYW5zYWN0aW9uVGltZSI6IjIwMjYtMDMtMDhUMTI6MzY6MzcuNjcwWiIsIk1ldGFkYXRhIjpudWxsLCJUcmFuc2FjdGlvbkluIjpudWxsLCJUcmFuc2FjdGlvbk91dCI6bnVsbH1dLCJDb3VudCI6MX0=\",\"Sign\":\"U1lTVEVNX0FfSU5DT01JTkc=\",\"SignerCert\":\"U1lTVEVNX0E=\"}"
```

Для Linux/macOS удобно сохранить JSON в файл `incoming.json` и выполнить:

```bash
curl -X POST "http://127.0.0.1:8000/api/messages/incoming" \
  -H "Content-Type: application/json" \
  -d @incoming.json
curl -X POST "https://est1-nikitagryn6043-lhk5p78z.leapcell.dev/api/messages/incoming" \
  -H "Content-Type: application/json" \
  -d @incoming.json
```

Ответ — подписанный объект `SignedApiData` с квитанциями (тип 215) при наличии в сообщениях поля `BankGuaranteeHash`.

**Пример ошибки (неверный хэш транзакции):** если в одной из транзакций поле `Hash` не совпадает с вычисленным, API вернёт `400` с текстом `Transaction hash mismatch`.

---

## Структура проекта

```
d:\Test1\
├── app.py              # Точка входа FastAPI: маршруты /api/health, /api/messages/outgoing, /api/messages/incoming
├── main.py             # Запуск uvicorn (host 0.0.0.0, port 8000, reload)
├── models.py           # Pydantic-модели: SignedApiData, Transaction, Message, SearchRequest, TransactionsData и др.
├── storage.py          # Хранилище транзакций в памяти (InMemoryStorage), список исходящих в SYSTEM_A
├── helpers.py          # Работа с подписью и Base64: compute_transaction_hash, build_signed_api_data, unpack_signed_api_data,
│                       # создание квитанций 215, кодирование/декодирование сообщений
├── test_data.py        # Инициализация тестовых данных при старте (пример сообщения 201 и транзакции)
├── requirements.txt    # Зависимости: fastapi, uvicorn[standard]
└── README.md           # Описание проекта, установка, curl-примеры, структура
```

### Назначение модулей

| Модуль | Назначение |
|--------|------------|
| **app.py** | REST API: health, приём входящих сообщений, выдача исходящих; валидация `SearchRequest` и `TransactionsData`, проверка хэша транзакций. |
| **models.py** | Контракты данных: подписанные обёртки, транзакции, сообщения, поисковые параметры. |
| **storage.py** | Реестр транзакций в памяти; добавление и выборка исходящих в SYSTEM_A за период с пагинацией. |
| **helpers.py** | ЭЦП (эмуляция), хэширование транзакций, формирование квитанций 215 и подписанных ответов. |
| **test_data.py** | Стартовая загрузка примера гарантии (201) для проверки эндпоинта исходящих сообщений. |

---

## Дополнительно

- После запуска сервера полное описание API доступно в Swagger UI: http://127.0.0.1:8000/docs .
