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
      <SearchBar
        v-model="searchQuery"
        class="header-search"
        @search="onSearch"
      />
    </div>

    <div class="header-right">
      <NuxtLink to="/users/" class="user-profile-link" title="Профиль">
       <UserAvatar 
          :id="user?.id"
          :full-name="user?.fullName" 
          :email="user?.email" 
        />
      </NuxtLink>
      <button class="icon-btn" @click="onNotifications" title="Уведомления">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5">
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
import { useUserProfile } from '~/composables/useUserProfile'

interface MenuItem {
  label: string
  to: string
  icon: string
  adminOnly?: boolean
}

export interface UserHeaderInfo {
  fullName?: string
  name?: string
  email?: string
  role?: string
}

const router = useRouter()
const route = useRoute()
const searchQuery = ref('')
const isMenuOpen = ref(true)

const defaultMenu: MenuItem[] = []

const filteredMenuItems = computed(() => {
  return (props.menuItems || defaultMenu).filter(
    item => !item.adminOnly || props.user?.role === 'admin'
  )
})

const props = defineProps<{
  user?: { fullName?: string; email?: string; role?: string; id?: string | number }
  menuItems?: MenuItem[]
}>()

const emit = defineEmits<{
  (e: 'navigate', query: string): void
  (e: 'search', query: string): void
  (e: 'navigate', item: any): void
}>()

const { isAdmin } = useUserProfile()

const isActive = (to: string) => {
  return route.path === to || (to !== '/' && route.path.startsWith(to + '/'))
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
  return
}

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
  updateSidebarWidthVariable()
}
</script>

<style scoped>
.app-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    padding: 0 24px;
    background: #ffffff;
    border-bottom: 1px solid var(--fluent-gray-40);
    z-index: 200;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;
}

.header-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--fluent-gray-100);
    margin: 0;
}

.search-wrapper {
    flex: 1;
    max-width: 480px;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;
}

.icon-btn {
    width: 32px;
    height: 32px;
    border-radius: 4px;
    border: none;
    background: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--fluent-gray-100);
    cursor: pointer;
    transition: background-color 0.15s;
}

.icon-btn:hover {
    background: var(--fluent-gray-20);
}

.burger-btn {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 16px;
    height: 12px;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 0;
}

.burger-line {
    display: block;
    width: 100%;
    height: 1.5px;
    background: var(--fluent-gray-100);
    border-radius: 1px;
    transition: transform 0.2s ease, opacity 0.2s ease;
}

.sidebar-menu {
    position: fixed;
    top: 60px;
    left: 0;
    bottom: 0;
    width: var(--sidebar-width);
    background: #f3f3f3;
    border-right: 1px solid #e5e5e5;
    padding: 12px 8px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    z-index: 150;
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow-x: hidden;
}

.mobile-nav {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.mobile-link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 12px;
    height: 36px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 400;
    color: #242424;
    text-decoration: none;
    white-space: nowrap;
    transition: background-color 0.1s ease;
}

.mobile-link .nav-icon {
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    color: #1a153b;
}

.mobile-link:hover {
    background: rgba(0, 0, 0, 0.04);
}

.mobile-link.active {
    background: #e2e2e2; 
    font-weight: 600;
}

.sidebar-menu.is-collapsed .link-label {
    display: none;
}

.user-profile-link {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #242424;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

@media (max-width: 768px) {
    .sidebar-menu {
        transform: translateX(-100%);
        width: 260px !important;
    }
    .sidebar-menu:not(.is-collapsed) {
        transform: translateX(0);
    }
}
</style>