# UDS Monitoring MADI

Веб-приложение для мониторинга состояния объектов УДС и управления рабочими процессами в рамках проекта ГТУ МАДИ. Проект объединяет backend API и frontend-интерфейс для работы с объектами, задачами, актами, дорожными картами и статусами выполнения работ.

## Что входит в проект

- Backend на FastAPI с модульной архитектурой
- Frontend на Nuxt 5 + Vue 3 + TypeScript
- Работа с PostgreSQL, Redis и MinIO
- Авторизация и защита API (JWT/CSRF)
- Миграции базы данных через Alembic
- Интерфейс для мониторинга и управления задачами и актами

## Технологический стек

- Python 3.12+
- FastAPI, Pydantic, SQLAlchemy, Dishka
- PostgreSQL, Redis, MinIO
- Alembic
- Nuxt 5, Vue 3, Pinia
- uv для управления Python-зависимостями
- pnpm для frontend-зависимостей

## Структура репозитория

- backend/ — серверная часть приложения, API, доменная логика и инфраструктура
- frontend/web platform road inspection/ — веб-интерфейс на Nuxt
- migrations/ — миграции базы данных
- main.py — точка входа backend-приложения
- alembic.ini — конфигурация Alembic

## Требования

- Python 3.12+
- Node.js 18+
- pnpm, npm, yarn или bun
- Docker/Compose (опционально, для локальной инфраструктуры)

## Быстрый старт

### 1. Backend

```bash
cd backend
uv sync
cd ..
python -m main
```

После запуска backend будет доступен по адресу:

- http://localhost:8000

### 2. Frontend

```bash
cd "frontend/web platform road inspection"
pnpm install
pnpm dev
```

После запуска frontend будет доступен по адресу:

- http://localhost:4000

### 3. Mock-режим для UI (по желанию)

Если нужно проверить интерфейс без полноценной backend-авторизации, можно запустить frontend в mock-режиме:

```bash
cd "frontend/web platform road inspection"
NUXT_PUBLIC_MOCK_AUTH=true pnpm dev
```

На Windows PowerShell:

```powershell
cd "frontend/web platform road inspection"
$env:NUXT_PUBLIC_MOCK_AUTH = "true"
pnpm dev
```

## База данных и миграции

Для применения миграций можно использовать Alembic из корня проекта:

```bash
alembic upgrade head
```

Для создания новой миграции:

```bash
alembic revision --autogenerate -m "описание_изменений"
```

## Разработка

- Backend-код организован по функциональным модулям: auth, data, filesystem и др.
- Frontend использует Nuxt, composables и Pinia для работы с состоянием приложения.
- При разработке рекомендуется запускать backend и frontend одновременно.

## Примечания

- Для работы с реальной авторизацией backend должен быть доступен на localhost:8000.
- Если frontend запускается на другом адресе, это следует учитывать в конфигурации API и callback URL.
