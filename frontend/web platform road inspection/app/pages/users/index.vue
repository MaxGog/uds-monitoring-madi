<template>
  <div class="monitoring-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">Управление пользователями</h2>
      </div>
      <div class="toolbar-right">
        <NuxtLink to="/users/create" class="btn-primary">+ Создать пользователя</NuxtLink>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">Загрузка пользователей...</div>
    <div v-else-if="error" class="error-banner">
      {{ error }}
      <button @click="fetchUsers" class="btn-retry">Повторить</button>
    </div>

    <div v-else class="table-card">
      <table class="fluent-table">
        <thead>
          <tr>
            <th>Пользователь</th>
            <th>Email</th>
            <th>Должность</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="users.length === 0">
            <td colspan="5" class="empty-cell">Пользователи не найдены</td>
          </tr>
          <tr v-for="user in users" :key="user.id">
            <td>
              <NuxtLink :to="`/users/${user.id}`" class="user-link">
                <UserAvatar :full-name="user.full_name || user.username" :email="user.email" :show-name="true" />
              </NuxtLink>
            </td>
            <td>{{ user.email }}</td>
            <td>{{ user.position || '—' }}</td>
            <td>
              <span :class="['status-badge', user.status]">
                {{ user.status }}
              </span>
            </td>
            <td>
              <NuxtLink :to="`/users/${user.id}`" class="btn-action">Открыть</NuxtLink>
              <button @click="handleDelete(user.id)" class="btn-action danger">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUser } from '~/composables/useUser'
import UserAvatar from '~/components/user_avatar.vue'

const { users, isLoading, error, fetchUsers, deleteUser } = useUser()

onMounted(() => {
  fetchUsers()
})

const handleDelete = async (id: string) => {
  if (confirm('Вы уверены, что хотите удалить пользователя?')) {
    await deleteUser(id)
  }
}
</script>

<style scoped>
.monitoring-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-family: var(--fluent-font, sans-serif);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 16px 24px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.table-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  overflow: hidden;
}

.fluent-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.fluent-table th, .fluent-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f3f3f3;
}

.fluent-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #605e5c;
}

.user-link {
  text-decoration: none;
  color: inherit;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  background: #e1dfdd;
}
.status-badge.active { background: #dff6dd; color: #107c41; }
.status-badge.inactive { background: #fde7e9; color: #a80000; }

.btn-primary {
  background-color: #0078d4;
  color: #ffffff;
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
}

.btn-action {
  background: none;
  border: none;
  color: #0078d4;
  cursor: pointer;
  margin-right: 8px;
  font-size: 12px;
  text-decoration: none;
}
.btn-action.danger { color: #a80000; }

.loading-state, .error-banner {
  padding: 24px;
  background: #fff;
  border-radius: 8px;
}
.error-banner { color: #a80000; }
.empty-cell { text-align: center; color: #8a8886; }
</style>