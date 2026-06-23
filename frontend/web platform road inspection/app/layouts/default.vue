<template>
  <div class="app-layout">
    <AppHeader
      :menu-items="menuItems"
      :user="currentUser"
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

const menuItems = [
  { label: 'Главная', to: '/', icon: '◆' },
  { label: 'Мониторинг', to: '/monitoring', icon: '⌂' },
  { label: 'Акты', to: '/acts', icon: '□' },
  { label: 'Статусы работ', to: '/work-statuses', icon: '▤' },
  { label: 'Дорожная карта', to: '/roadmap', icon: '◫' },
  { label: 'Задачи', to: '/tasks', icon: '☑' },
  { label: 'Карточки по титулу', to: '/title-cards', icon: '▥' },
  { label: 'Пользователи', to: '/users', icon: '👤', adminOnly: true },
]

// Пример текущего пользователя
const currentUser = ref({
  fullName: 'Пользователь',
  email: 'user@example.com',
  role: 'Администратор',
})

const handleSearch = (query: string) => {
  console.log('Поиск:', query)
  // здесь можно обновить глобальный стейт или перенаправить
}

const handleNavigate = (item: any) => {
  console.log('Переход на', item.label)
}
</script>

<style>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.main-content {
  flex: 1;
  padding: 24px 32px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}
</style>