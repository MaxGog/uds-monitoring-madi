<template>
  <div class="monitoring-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">Управление пользователями</h2>
        <span v-if="!isLoading && !error" class="user-count-badge">
          {{ filteredUsers.length }} {{ getUsersCountLabel(filteredUsers.length) }}
        </span>
      </div>
      <div class="toolbar-right">
        <div class="search-box">
          <svg class="search-icon" viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
          </svg>
          <input 
            v-model="searchQuery" 
            type="text" 
            class="fluent-search-input" 
            placeholder="Поиск пользователей..." 
          />
          <button v-if="searchQuery" @click="searchQuery = ''" class="search-clear-btn" title="Очистить">✕</button>
        </div>

        <NuxtLink to="/users/create" class="btn-primary">
          <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
            <path d="M8 2a.75.75 0 0 1 .75.75v4.5h4.5a.75.75 0 0 1 0 1.5h-4.5v4.5a.75.75 0 0 1-1.5 0v-4.5h-4.5a.75.75 0 0 1 0-1.5h4.5v-4.5A.75.75 0 0 1 8 2z"/>
          </svg>
          <span>Создать пользователя</span>
        </NuxtLink>
      </div>
    </div>

    <div v-if="isLoading" class="shimmer-card">
      <div class="shimmer-row" v-for="n in 5" :key="n">
        <div class="shimmer-block avatar"></div>
        <div class="shimmer-block text-long"></div>
        <div class="shimmer-block text-short"></div>
        <div class="shimmer-block status"></div>
      </div>
    </div>

    <div v-else-if="error" class="error-banner" role="alert">
      <div class="error-content">
        <svg class="error-icon" viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
          <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
          <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995z"/>
        </svg>
        <span>{{ error }}</span>
      </div>
      <button @click="fetchUsers" class="btn-retry">Повторить попытку</button>
    </div>

    <div v-else class="table-card">
      <table class="fluent-table">
        <thead>
          <tr>
            <th>Пользователь</th>
            <th>Email</th>
            <th>Должность</th>
            <th>Компания</th>
            <th>Статус</th>
            <th class="actions-column">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredUsers.length === 0">
            <td colspan="6" class="empty-cell">
              <div class="empty-state">
                <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
                <p class="empty-title">Пользователи не найдены</p>
                <p class="empty-subtitle" v-if="searchQuery">Попробуйте изменить поисковый запрос</p>
              </div>
            </td>
          </tr>

          <tr v-for="user in filteredUsers" :key="user.id" class="table-row">
            <td>
              <NuxtLink :to="`/users/${user.id}`" class="user-link">
                <UserAvatar :full-name="user.full_name || user.username" :email="user.email" :show-name="true" />
              </NuxtLink>
            </td>
            <td class="secondary-text">{{ user.email }}</td>
            <td class="secondary-text">{{ user.position || '—' }}</td>
            <td class="secondary-text">{{ user.company || '—' }}</td>
            <td>
              <span :class="['status-badge', getStatusClass(user.status)]">
                <span class="status-dot"></span>
                {{ formatStatus(user.status) }}
              </span>
            </td>
            <td class="actions-column">
              <div class="action-buttons">
                <NuxtLink :to="`/users/${user.id}`" class="btn-action" title="Просмотреть профиль">
                  <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
                    <path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/>
                    <path d="M0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8zm8 3.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z"/>
                  </svg>
                  <span>Открыть</span>
                </NuxtLink>
                <button @click="handleDelete(user.id)" class="btn-action danger" title="Удалить">
                  <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                    <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                  </svg>
                  <span>Удалить</span>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUser } from '~/composables/useUser'
import UserAvatar from '~/components/user_avatar.vue'

const { users, isLoading, error, fetchUsers, deleteUser } = useUser()
const searchQuery = ref('')

onMounted(() => {
  fetchUsers()
})

const filteredUsers = computed(() => {
  if (!searchQuery.value.trim()) return users.value
  const q = searchQuery.value.toLowerCase()
  return users.value.filter(u => 
    (u.full_name && u.full_name.toLowerCase().includes(q)) ||
    (u.email && u.email.toLowerCase().includes(q)) ||
    (u.username && u.username.toLowerCase().includes(q)) ||
    (u.position && u.position.toLowerCase().includes(q))
  )
})

const getUsersCountLabel = (count: number) => {
  const remainder10 = count % 10
  const remainder100 = count % 100
  if (remainder10 === 1 && remainder100 !== 11) return 'пользователь'
  if ([2, 3, 4].includes(remainder10) && ![12, 13, 14].includes(remainder100)) return 'пользователя'
  return 'пользователей'
}

const getStatusClass = (status: string) => {
  if (!status) return 'default'
  const lower = status.toLowerCase()
  if (lower === 'active' || lower === 'активен') return 'active'
  if (lower === 'inactive' || lower === 'заблокирован' || lower === 'disabled') return 'inactive'
  return 'pending'
}

const formatStatus = (status: string) => {
  if (!status) return 'Неизвестно'
  const lower = status.toLowerCase()
  if (lower === 'active') return 'Активен'
  if (lower === 'inactive') return 'Заблокирован'
  if (lower === 'pending') return 'В ожидании'
  return status
}

const handleDelete = async (id: string) => {
  if (confirm('Вы уверены, что хотите удалить этого пользователя?')) {
    await deleteUser(id)
  }
}
</script>

<style scoped>
.monitoring-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-family: 'Segoe UI', var(--fluent-font, system-ui, -apple-system, sans-serif);
  color: #242424;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 12px 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #242424;
  margin: 0;
}

.user-count-badge {
  font-size: 12px;
  font-weight: 600;
  color: #605e5c;
  background: #f3f2f1;
  padding: 2px 8px;
  border-radius: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 10px;
  color: #605e5c;
  pointer-events: none;
}

.fluent-search-input {
  border: 1px solid #8a8886;
  border-bottom: 2px solid #605e5c;
  border-radius: 4px;
  height: 32px;
  padding: 0 30px;
  font-size: 13px;
  box-sizing: border-box;
  font-family: inherit;
  background: #ffffff;
  width: 220px;
  transition: border-color 0.15s ease, width 0.2s ease;
}

.fluent-search-input:focus {
  outline: none;
  border-color: #0078d4;
  border-bottom-color: #0078d4;
  box-shadow: 0 0 0 1px #0078d4;
  width: 260px;
}

.search-clear-btn {
  position: absolute;
  right: 6px;
  background: transparent;
  border: none;
  color: #605e5c;
  cursor: pointer;
  padding: 2px 6px;
  font-size: 12px;
  border-radius: 2px;
}
.search-clear-btn:hover { background: #f3f3f3; color: #242424; }

.btn-primary {
  background-color: #0078d4;
  color: #ffffff;
  padding: 0 16px;
  height: 32px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.1s ease;
}
.btn-primary:hover { background-color: #106ebe; }
.btn-primary:active { background-color: #005a9e; }

.table-card {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.fluent-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.fluent-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #605e5c;
  padding: 10px 16px;
  border-bottom: 1px solid #e0e0e0;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.fluent-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #f3f2f1;
  vertical-align: middle;
}

.table-row {
  transition: background-color 0.1s ease;
}

.table-row:hover {
  background-color: #f5f5f5;
}

.user-link {
  text-decoration: none;
  color: inherit;
  display: inline-block;
}

.user-link:hover {
  color: #0078d4;
}

.secondary-text {
  color: #605e5c;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.status-badge.active {
  background-color: #dff6dd;
  color: #107c41;
}

.status-badge.inactive {
  background-color: #fde7e9;
  color: #a80000;
}

.status-badge.pending {
  background-color: #fff4ce;
  color: #797775;
}

.status-badge.default {
  background-color: #f3f2f1;
  color: #605e5c;
}

.actions-column {
  text-align: right;
  width: 160px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: 1px solid transparent;
  color: #0078d4;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.1s ease, border-color 0.1s ease;
}

.btn-action:hover {
  background-color: #eff6fc;
  border-color: #c7e0f4;
}

.btn-action.danger {
  color: #a80000;
}

.btn-action.danger:hover {
  background-color: #fde7e9;
  border-color: #fce8e6;
}

/* Empty State */
.empty-cell {
  padding: 40px 16px !important;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #a19f9d;
}

.empty-title {
  font-size: 14px;
  font-weight: 600;
  color: #605e5c;
  margin: 8px 0 2px 0;
}

.empty-subtitle {
  font-size: 12px;
  margin: 0;
}

.error-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fde7e9;
  border-left: 4px solid #a80000;
  color: #a80000;
  padding: 12px 16px;
  border-radius: 4px;
  font-size: 13px;
}

.error-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-retry {
  background: #ffffff;
  border: 1px solid #a80000;
  color: #a80000;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.btn-retry:hover { background: #fde7e9; }

/* Shimmer / Skeleton Loader */
.shimmer-card {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.shimmer-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.shimmer-block {
  background: linear-gradient(90deg, #f3f2f1 25%, #edebe9 50%, #f3f2f1 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  height: 16px;
}

.shimmer-block.avatar { width: 32px; height: 32px; border-radius: 50%; }
.shimmer-block.text-long { flex: 2; }
.shimmer-block.text-short { flex: 1; }
.shimmer-block.status { width: 80px; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>