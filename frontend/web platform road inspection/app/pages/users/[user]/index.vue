<template>
  <div class="monitoring-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <NuxtLink to="/users" class="btn-back" title="Назад к списку">
          <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
            <path fill-rule="evenodd" d="M15 8a.75.75 0 0 1-.75.75H4.31l3.72 3.72a.75.75 0 1 1-1.06 1.06l-5-5a.75.75 0 0 1 0-1.06l5-5a.75.75 0 0 1 1.06 1.06L4.31 7.25H14.25A.75.75 0 0 1 15 8z"/>
          </svg>
          <span>К списку пользователей</span>
        </NuxtLink>
      </div>

      <div class="toolbar-right" v-if="currentUser && !isLoading">
        <NuxtLink :to="`/users/${userId}/edit`" class="btn-secondary">
          <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
            <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-9.8 9.8a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l9.8-9.8zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5.5 13V12.5a.5.5 0 0 1-.5-.5V11.5a.5.5 0 0 1-.5-.5H4a.5.5 0 0 1-.481-.325z"/>
          </svg>
          <span>Редактировать</span>
        </NuxtLink>
        <button @click="handleDelete" class="btn-action danger">
          <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
            <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
          </svg>
          <span>Удалить</span>
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="profile-card shimmer-card">
      <div class="shimmer-header">
        <div class="shimmer-avatar"></div>
        <div class="shimmer-info">
          <div class="shimmer-line title"></div>
          <div class="shimmer-line subtitle"></div>
        </div>
      </div>
      <div class="shimmer-body">
        <div class="shimmer-line" v-for="n in 6" :key="n"></div>
      </div>
    </div>

    <div v-else-if="error" class="error-banner" role="alert">
      <span>{{ error }}</span>
      <button @click="fetchUser(userId)" class="btn-retry">Повторить</button>
    </div>

    <div v-else-if="currentUser" class="profile-container">
      <div class="profile-card persona-header">
        <div class="persona-main">
          <UserAvatar 
            :full-name="currentUser.full_name || currentUser.username" 
            :email="currentUser.email" 
            class="large-avatar"
          />
        </div>
        <div class="persona-status">
          <span :class="['status-badge', getStatusClass(currentUser.status)]">
            <span class="status-dot"></span>
            {{ formatStatus(currentUser.status) }}
          </span>
        </div>
      </div>

      <div class="details-grid">
        <div class="profile-card detail-card">
          <h3 class="card-section-title">Личные и контактные данные</h3>
          <div class="detail-list">
            <div class="detail-item">
              <span class="detail-label">ФИО сотрудника</span>
              <span class="detail-value">{{ currentUser.full_name || '—' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Логин (Username)</span>
              <span class="detail-value highlight">@{{ currentUser.username }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Рабочий Email</span>
              <a :href="`mailto:${currentUser.email}`" class="detail-value link">{{ currentUser.email }}</a>
            </div>
            <div class="detail-item">
              <span class="detail-label">Должность</span>
              <span class="detail-value">{{ currentUser.position || '—' }}</span>
            </div>
          </div>
        </div>

        <div class="profile-card detail-card">
          <h3 class="card-section-title">Организация и доступ</h3>
          <div class="detail-list">
            <div class="detail-item">
              <span class="detail-label">Компания / Организация</span>
              <span class="detail-value">{{ currentUser.company || '—' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Системная роль</span>
              <span class="role-pill">{{ formatRole(currentUser.role) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">ID пользователя</span>
              <span class="detail-value code">{{ currentUser.id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Дата регистрации</span>
              <span class="detail-value">{{ formatDate(currentUser.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUser } from '~/composables/useUser'
import UserAvatar from '~/components/user_avatar.vue'

const route = useRoute()
const router = useRouter()
const userId = route.params.user as string

const { currentUser, isLoading, error, fetchUser, deleteUser } = useUser()

onMounted(() => {
  if (userId) {
    fetchUser(userId)
  }
})

const handleDelete = async () => {
  if (confirm('Вы уверены, что хотите удалить этого пользователя?')) {
    const success = await deleteUser(userId)
    if (success) {
      router.push('/users')
    }
  }
}

const getStatusClass = (status: string) => {
  if (!status) return 'default'
  const lower = status.toLowerCase()
  if (lower === 'active' || lower === 'активен') return 'active'
  if (lower === 'inactive' || lower === 'заблокирован') return 'inactive'
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

const formatRole = (role: string) => {
  const rolesMap: Record<string, string> = {
    admin: 'Администратор',
    engineer: 'Инженер технадзора',
    viewer: 'Наблюдатель'
  }
  return rolesMap[role] || role || 'Не указана'
}

const formatDate = (dateString?: string) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
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
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #0078d4;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  padding: 6px 10px;
  border-radius: 4px;
  transition: background-color 0.1s ease;
}
.btn-back:hover { background-color: #f3f3f3; }

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1px solid #d1d1d1;
  height: 32px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  color: #242424;
  text-decoration: none;
  transition: background-color 0.1s ease;
}
.btn-secondary:hover { background: #f5f5f5; }

.btn-action.danger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: 1px solid #fce8e6;
  color: #a80000;
  padding: 0 12px;
  height: 32px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.1s ease;
}
.btn-action.danger:hover { background-color: #fde7e9; }

.profile-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 900px;
}

.profile-card {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  padding: 24px;
}

.persona-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.persona-main {
  display: flex;
  align-items: center;
  gap: 20px;
}

.persona-name {
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #242424;
}

.persona-position {
  font-size: 14px;
  color: #605e5c;
  margin: 0 0 2px 0;
}

.persona-company {
  font-size: 13px;
  color: #0078d4;
  margin: 0;
  font-weight: 600;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}
.status-dot { width: 6px; height: 6px; border-radius: 50%; background-color: currentColor; }
.status-badge.active { background-color: #dff6dd; color: #107c41; }
.status-badge.inactive { background-color: #fde7e9; color: #a80000; }
.status-badge.pending { background-color: #fff4ce; color: #797775; }

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 768px) {
  .details-grid { grid-template-columns: 1fr; }
  .persona-header { flex-direction: column; gap: 16px; }
}

.card-section-title {
  font-size: 13px;
  font-weight: 600;
  color: #0078d4;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f3f2f1;
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: #605e5c;
  font-weight: 600;
}

.detail-value {
  font-size: 14px;
  color: #242424;
}

.detail-value.highlight { font-weight: 600; color: #3b3a39; }
.detail-value.link { color: #0078d4; text-decoration: none; }
.detail-value.link:hover { text-decoration: underline; }
.detail-value.code { font-family: monospace; font-size: 12px; color: #605e5c; }

.role-pill {
  display: inline-block;
  align-self: flex-start;
  background: #f3f2f1;
  border: 1px solid #e0e0e0;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #3b3a39;
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
}
.btn-retry {
  background: #ffffff;
  border: 1px solid #a80000;
  color: #a80000;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.shimmer-card { display: flex; flex-direction: column; gap: 20px; }
.shimmer-header { display: flex; gap: 16px; align-items: center; }
.shimmer-avatar { width: 56px; height: 56px; border-radius: 50%; background: #edebe9; }
.shimmer-info { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.shimmer-line { height: 14px; background: #edebe9; border-radius: 4px; }
.shimmer-line.title { width: 40%; height: 20px; }
.shimmer-line.subtitle { width: 25%; }
.shimmer-body { display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
</style>