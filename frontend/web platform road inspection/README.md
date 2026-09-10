# Frontend — Road Inspection UI

Интерфейс проекта мониторинга УДС на Nuxt 5.

## Описание

Это фронтенд-часть веб-приложения для управления объектами, задачами и мониторинга состояния дорожной инфраструктуры.

## Требования

- Node.js 18+ или совместимая версия
- npm / pnpm / yarn / bun
- backend-сервис на `http://localhost:8000` для реальной авторизации и работы API

## Установка

```bash
# npm
npm install

# pnpm
pnpm install

# yarn
yarn install

# bun
bun install
```

## Запуск в режиме разработки

Фронтенд по умолчанию запускается на:

```bash
http://localhost:4000
```

```bash
# npm
npm run dev

# pnpm
pnpm dev

# yarn
yarn dev

# bun
bun run dev
```

## Mock auth (тестирование UI без бэкенда)

Если нужно проверить интерфейс без реальной авторизации, включите mock-режим.

```bash
export NUXT_PUBLIC_MOCK_AUTH=true
npm run dev
```

На Windows PowerShell:

```powershell
$env:NUXT_PUBLIC_MOCK_AUTH = 'true'
npm run dev
```

После запуска откройте `/login` и используйте кнопку `Локальный вход (Bypass)`.

В этом режиме фронтенд сохраняет токен в cookie и mock-пользователя в `localStorage`, что позволяет работать с UI без реального login flow.

## Сценарии работы

- **Без mock-режима** — приложение ожидает реальную авторизацию через backend OAuth / PKCE.
- **С mock-режимом** — кнопка локального входа доступна, и приложение сохраняет mock-данные на клиенте.

## Сборка и предпросмотр

```bash
# npm
npm run build
npm run preview

# pnpm
pnpm build
pnpm preview

# yarn
yarn build
yarn preview

# bun
bun run build
bun run preview
```

## Полезные ссылки

- API backend: `http://localhost:8000`
- Фронтенд: `http://localhost:4000`

## Примечания

- Если бэкенд запущен на другом адресе, настройте соответствующие URL в коде и окружении.
- Для mock-auth используется переменная `NUXT_PUBLIC_MOCK_AUTH=true`.
- Фронтенд ожидает callback URL `http://localhost:4000/login/callback` при реальной авторизации.
