<template>
  <header class="app-header">
    <div class="header-left">
      <button class="burger-btn" @click="toggleMenu" aria-label="Меню">
        <span class="burger-line" :class="{ active: isMenuOpen }"></span>
        <span class="burger-line" :class="{ active: isMenuOpen }"></span>
        <span class="burger-line" :class="{ active: isMenuOpen }"></span>
      </button>
      
      <h1 class="header-title">Мониторинг состояния объектов УДС</h1>
    </div>

    <div class="search-wrapper">
      <span class="search-icon">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="7" />
          <path d="M16 16l4 4" />
        </svg>
      </span>
      <SearchBar
        v-model="searchQuery"
        class="header-search"
        @search="onSearch"
      />
    </div>

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

  <aside class="sidebar-menu" :class="{ 'is-collapsed': !isMenuOpen }">
    <nav class="mobile-nav">
      <NuxtLink
        v-for="item in filteredMenuItems"
        :key="item.to"
        :to="item.to"
        class="mobile-link"
        :class="{ active: isActive(item.to) }"
        :title="!isMenuOpen ? item.label : ''"
        @click="onMobileNavigate(item)"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="link-label" v-if="isMenuOpen">{{ item.label }}</span>
      </NuxtLink>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from '#app'
import SearchBar from '~/components/search_bar.vue'
import UserAvatar from '~/components/user_avatar.vue'

interface MenuItem {
  label: string
  to: string
  icon: string
  adminOnly?: boolean
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
const isMenuOpen = ref(true)

const defaultMenu: MenuItem[] = [
  { label: 'Главная', to: '/', icon: '🏠' },
  { label: 'Мониторинг объектов', to: '/monitoring', icon: '📊' },
  { label: 'Работа с актами', to: '/acts', icon: '📄' },
  { label: 'Статусы работ', to: '/work-statuses', icon: '📈' },
  { label: 'Формирование ДК', to: '/roadmap', icon: '🗺️' },
  { label: 'Задачи', to: '/tasks', icon: '✔️' },
  { label: 'Пользователи', to: '/users', icon: '👤', adminOnly: true },
]

const filteredMenuItems = computed(() => {
  const base = props.menuItems?.length ? props.menuItems : defaultMenu
  return base.filter(item => !item.adminOnly || props.user?.role === 'Администратор')
})

const isActive = (to: string) => {
  return route.path === to || route.path.startsWith(to + '/')
}

const updateSidebarWidthVariable = () => {
  if (typeof window !== 'undefined' && document.documentElement) {
    document.documentElement.style.setProperty('--sidebar-width', isMenuOpen.value ? '260px' : '64px')
  }
}

onMounted(() => {
  updateSidebarWidthVariable()
})

const onMobileNavigate = (item: MenuItem) => {
  emit('navigate', item)
  router.push(item.to)
}

const onSearch = () => {
  emit('search', searchQuery.value)
}

const onNotifications = () => {
  emit('notifications')
}

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
  updateSidebarWidthVariable()
}
</script>