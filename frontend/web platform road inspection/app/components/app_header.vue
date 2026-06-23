<template>
  <header class="app-header">
    <div class="header-left">
      <div class="brand">
        <div class="brand-icon">▮</div>
        <div class="brand-text">
          <span class="brand-title">Мониторинг состояния объектов УДС</span>
        </div>
      </div>

      <nav class="nav-menu">
        <NuxtLink
          v-for="item in menuItems"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          :class="{ active: isActive(item.to) }"
          @click="onNavigate(item)"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          {{ item.label }}
        </NuxtLink>
      </nav>
    </div>

    <SearchBar
      v-model="searchQuery"
      class="header-search"
      @search="onSearch"
    />

    <div class="header-right">
      <UserAvatar :full-name="user?.fullName" :email="user?.email" show-name />
      <button class="icon-btn" @click="onNotifications" title="Уведомления">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from '#app'

interface MenuItem {
  label: string
  to: string
  icon: string
}

const props = defineProps<{
  menuItems?: MenuItem[]
  user?: { fullName?: string; email?: string; role?: string }
}>()

const emit = defineEmits<{
  (e: 'navigate', item: MenuItem): void
  (e: 'search', query: string): void
  (e: 'notifications'): void
}>()

const router = useRouter()
const route = useRoute()

const searchQuery = ref('')

const defaultMenu: MenuItem[] = [
  { label: 'Главная', to: '/', icon: '🏠' },
  { label: 'Мониторинг', to: '/monitoring', icon: '🕶️' },
  { label: 'Акты', to: '/acts', icon: '📄' },
  { label: 'Статусы работ', to: '/work-statuses', icon: '📊' },
  { label: 'Дорожная карта', to: '/roadmap', icon: '🗺️' },
  { label: 'Задачи', to: '/tasks', icon: '✔️' },
  { label: 'Карточки по титулу', to: '/title-cards', icon: '▥' },
  { label: 'Пользователи', to: '/users', icon: '👤', adminOnly: true },
]

const menuItems = computed(() => {
  const items = props.menuItems?.length ? props.menuItems : defaultMenu
  return items.filter(item => !item.adminOnly || props.user?.role === 'Администратор')
})

const isActive = (to: string) => {
  return route.path === to || route.path.startsWith(to + '/')
}

const onNavigate = (item: MenuItem) => {
  emit('navigate', item)
  router.push(item.to)
}

const onSearch = () => {
  emit('search', searchQuery.value)
}

const onNotifications = () => {
  emit('notifications')
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 12px 32px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--line, #e8ebf5);
  box-shadow: 0 8px 32px rgba(34, 29, 84, 0.06);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 32px;
  flex-shrink: 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--violet, #6752f5), var(--violet-2, #8a6cff));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  box-shadow: 0 6px 16px rgba(103, 82, 245, 0.25);
}
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.brand-title {
  font-weight: 800;
  font-size: 16px;
  color: var(--text, #14133b);
}
.brand-sub {
  font-weight: 600;
  font-size: 12px;
  color: var(--muted, #737895);
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 30px;
  font-weight: 700;
  font-size: 14px;
  color: var(--muted, #737895);
  text-decoration: none;
  transition: background 0.2s, color 0.2s, transform 0.1s;
  cursor: pointer;
  white-space: nowrap;
}
.nav-link .nav-icon {
  font-size: 16px;
}
.nav-link:hover {
  background: rgba(103, 82, 245, 0.06);
  color: var(--violet, #6752f5);
  transform: translateY(-1px);
}
.nav-link.active {
  background: linear-gradient(135deg, var(--violet, #6752f5), var(--violet-2, #8a6cff));
  color: #fff;
  box-shadow: 0 8px 20px rgba(103, 82, 245, 0.25);
}
.nav-link.active:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(103, 82, 245, 0.35);
}

.header-search {
  flex: 1;
  max-width: 480px;
  margin: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.icon-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--line, #e8ebf5);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--muted, #737895);
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
}
.icon-btn:hover {
  background: rgba(103, 82, 245, 0.06);
  border-color: var(--violet, #6752f5);
  color: var(--violet, #6752f5);
  box-shadow: 0 4px 12px rgba(103, 82, 245, 0.12);
}

/* Адаптивность */
@media (max-width: 1100px) {
  .app-header {
    flex-wrap: wrap;
    padding: 12px 20px;
    gap: 12px;
  }
  .header-left {
    width: 100%;
    justify-content: space-between;
  }
  .nav-menu {
    display: none;
  }
  .header-search {
    order: 3;
    flex-basis: 100%;
    max-width: 100%;
    margin: 0;
  }
  .header-right {
    margin-left: auto;
  }
}

@media (max-width: 600px) {
  .brand-text .brand-sub {
    display: none;
  }
  .header-right .user-name {
    display: none;
  }
}
</style>