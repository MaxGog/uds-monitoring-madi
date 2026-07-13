<template>
  <div class="monitoring-page">
    <div class="toolbar">
      <NuxtLink to="/users" class="btn-back">⬅ Назад к списку</NuxtLink>
      <h2 class="page-title">Профиль пользователя</h2>
    </div>

    <div v-if="isLoading" class="state-card">Загрузка данных...</div>
    <div v-else-if="error" class="state-card error">{{ error }}</div>

    <div v-else-if="currentUser" class="user-card">
      <div class="user-header">
        <UserAvatar 
          :full-name="currentUser.full_name || currentUser.username" 
          :email="currentUser.email" 
        />
        <div class="user-header-info">
          <h3>{{ currentUser.full_name || currentUser.username }}</h3>
          <p class="role-subtitle">{{ currentUser.position || 'Должность не указана' }}</p>
        </div>
      </div>

      <div class="user-details">
        <div class="detail-item">
          <label>Email</label>
          <span>{{ currentUser.email }}</span>
        </div>
        <div class="detail-item">
          <label>Имя пользователя</label>
          <span>{{ currentUser.username }}</span>
        </div>
        <div class="detail-item">
          <label>Статус</label>
          <span class="status">{{ currentUser.status }}</span>
        </div>
        <div class="detail-item">
          <label>Дата регистрации</label>
          <span>{{ new Date(currentUser.created_at).toLocaleDateString('ru-RU') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUser } from '~/composables/useUser'
import UserAvatar from '~/components/user_avatar.vue'

const route = useRoute()
const userId = route.params.user as string

const { currentUser, isLoading, error, fetchUser } = useUser()

onMounted(() => {
  if (userId) {
    fetchUser(userId)
  }
})
</script>

<style scoped>
.monitoring-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #ffffff;
  padding: 16px 24px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
}

.btn-back {
  color: #0078d4;
  text-decoration: none;
  font-size: 14px;
}

.user-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  padding: 24px;
  max-width: 600px;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eaeaea;
}

.user-header-info h3 {
  margin: 0;
  font-size: 18px;
}

.role-subtitle {
  margin: 4px 0 0 0;
  color: #605e5c;
  font-size: 13px;
}

.user-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-size: 12px;
  color: #605e5c;
  font-weight: 600;
}

.detail-item span {
  font-size: 14px;
}

.state-card {
  background: #ffffff;
  padding: 24px;
  border-radius: 8px;
}
.state-card.error { color: #a80000; }
</style>