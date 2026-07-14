<template>
  <div class="app-layout">
    <app-header
      :menu-items="menuItems"
      :user="currentUser!"
      @search="handleSearch"
      @navigate="handleNavigate"
    />
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { apiFetch } from '~/composables/useAPI'

const { user: authUser } = useAuth()

const currentUser = computed(() => {
  if (!authUser.value) return null

  const fullName = authUser.value.name || authUser.value.email || 'Пользователь'

  const roleName = typeof authUser.value.role === 'object' 
    ? (authUser.value.role as any)?.name 
    : authUser.value.role

  return {
    fullName: fullName,
    email: authUser.value.email,
    role: roleName
  }
})

onMounted(async () => {
  if (authUser.value && !authUser.value.name) {
    try {
      const response = await apiFetch<any>('/users/me')
      if (response?.data) {
        const data = response.data
        const fullName = [data.first_name, data.last_name].filter(Boolean).join(' ') || data.email
        authUser.value = {
          ...authUser.value,
          name: fullName
        }
      }
    } catch (err) {
      console.error('Ошибка при получении профиля:', err)
    }
  }
})

const menuItems = [
  { label: 'Главная', to: '/', icon: '🏠' },
  { label: 'Мониторинг объектов', to: '/monitoring', icon: '📊' },
  { label: 'Работа с актами', to: '/acts', icon: '📄' },
  { label: 'Статусы работ', to: '/work-statuses', icon: '📈' },
  { label: 'Формирование ДК', to: '/roadmap', icon: '🗺️' },
  { label: 'Задачи', to: '/tasks', icon: '✔️' },
  { label: 'Пользователи', to: '/users', icon: '👤', adminOnly: true },
]

const handleSearch = (query: string) => {
  console.log('Поиск:', query)
}

const handleNavigate = (item: any) => {
  console.log('Переход на', item.label)
}
</script>

<style>
/* Глобальные переменные Fluent темы на уровне приложения */
:root {
  --fluent-blue: #0078d4;
  --fluent-gray-10: #f3f4f6; /* цвет сайдбара */
  --fluent-gray-20: #eaeaea; /* ховер */
  --fluent-gray-30: #e1e3e8; /* активный пункт меню на скриншоте */
  --fluent-gray-40: #e1e3e8; /* границы */
  --fluent-gray-100: #242424; /* основной текст */
  --fluent-text-muted: #616161; /* подписи */
  --fluent-font: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
  --sidebar-width: 260px;
}

body {
  margin: 0;
  font-family: var(--fluent-font);
  background-color: #f5f5f5;
}

.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  margin-top: 60px;
  margin-left: var(--sidebar-width);
  padding: 24px;
  min-height: calc(100vh - 60px);
  box-sizing: border-box;
  background-color: #f5f5f5;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
}
</style>