<template>
  <div class="monitoring-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <NuxtLink :to="`/users/${userId}`" class="btn-back" title="Назад к профилю">
          <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
            <path fill-rule="evenodd" d="M15 8a.75.75 0 0 1-.75.75H4.31l3.72 3.72a.75.75 0 1 1-1.06 1.06l-5-5a.75.75 0 0 1 0-1.06l5-5a.75.75 0 0 1 1.06 1.06L4.31 7.25H14.25A.75.75 0 0 1 15 8z"/>
          </svg>
          <span>К профилю пользователя</span>
        </NuxtLink>
        <h2 class="page-title">Редактирование профиля</h2>
      </div>
    </div>

    <div v-if="isLoading && !isSubmitting" class="form-card shimmer-loader">
      Загрузка данных пользователя...
    </div>

    <div v-else class="form-card">
      <form @submit.prevent="submitForm" class="fluent-form">
        <div v-if="error" class="error-banner" role="alert">
          <span>{{ error }}</span>
        </div>

        <h3 class="form-section-title">Основная информация</h3>
        <div class="form-row">
          <div class="form-group">
            <label>ФИО сотрудника</label>
            <input 
              v-model="form.full_name" 
              type="text" 
              class="fluent-input" 
              placeholder="Иванов Петр Сергеевич" 
            />
          </div>
          <div class="form-group">
            <label>Имя пользователя (Username) *</label>
            <input 
              v-model="form.username" 
              type="text" 
              class="fluent-input" 
              placeholder="p.ivanov" 
              required 
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Рабочий Email *</label>
            <input 
              v-model="form.email" 
              type="email" 
              class="fluent-input" 
              placeholder="p.ivanov@company.ru" 
              required 
            />
          </div>
          <div class="form-group">
            <label>Должность</label>
            <input 
              v-model="form.position" 
              type="text" 
              class="fluent-input" 
              placeholder="Главный специалист" 
            />
          </div>
        </div>

        <h3 class="form-section-title">Организация и Доступ</h3>
        <div class="form-row">
          <div class="form-group">
            <label>Компания / Организация</label>
            <select v-model="form.company" class="fluent-select">
              <option v-for="comp in companiesList" :key="comp" :value="comp">{{ comp }}</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Роль в системе *</label>
            <select v-model="form.role" class="fluent-select" required>
              <option v-for="r in rolesList" :key="r.value" :value="r.value">{{ r.label }}</option>
            </select>
          </div>
        </div>

        <!-- Новый блок: Безопасность (Пароль) -->
        <h3 class="form-section-title">Безопасность</h3>
        <div class="form-row">
          <div class="form-group">
            <label>Новый пароль</label>
            <div class="password-input-wrapper">
              <input 
                v-model="form.password" 
                :type="showPassword ? 'text' : 'password'" 
                class="fluent-input password-input" 
                placeholder="Оставьте пустым, если не хотите менять" 
                autocomplete="new-password"
              />
              <button 
                type="button" 
                class="btn-toggle-password" 
                @click="showPassword = !showPassword"
                :title="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
              >
                <!-- Иконка глаза -->
                <svg v-if="!showPassword" viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
                  <path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/>
                  <path d="M0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8zm8 3.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z"/>
                </svg>
                <!-- Перечеркнутый глаз -->
                <svg v-else viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
                  <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c3.84 0 6.6 3.58 7.37 4.5a10.05 10.05 0 0 1-2.7 2.723l.689.688zM1.354 1.354a.5.5 0 0 0-.708.708l13 13a.5.5 0 0 0 .708-.708l-13-13z"/>
                  <path d="M1.147 4.108A9.97 9.97 0 0 0 0 8s3 5.5 8 5.5a7.027 7.027 0 0 0 3.25-.792l-.734-.734A5.928 5.928 0 0 1 8 12.5c-3.84 0-6.6-3.58-7.37-4.5a10.13 10.13 0 0 1 1.763-2.181l-.689-.688z"/>
                </svg>
              </button>
            </div>
            <span class="field-hint">Заполняйте только при необходимости смены пароля</span>
          </div>
        </div>

        <div class="form-actions">
          <NuxtLink :to="`/users/${userId}`" class="btn-secondary">Отмена</NuxtLink>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner"></span>
            <span>{{ isSubmitting ? 'Сохранение...' : 'Сохранить изменения' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUser } from '~/composables/useUser'
import type { UserUpdate } from '~/types/user'

const route = useRoute()
const router = useRouter()
const userId = route.params.user as string

const { currentUser, isLoading, error, fetchUser, updateUser } = useUser()
const isSubmitting = ref(false)
const showPassword = ref(false)

const companiesList = [
  'ООО "ТехноМониторинг"',
  'АО "СтройКонтроль"',
  'ГБУ "Автодор-МАДИ"'
]

const rolesList = [
  { value: 'admin', label: 'Администратор' },
  { value: 'engineer', label: 'Инженер технадзора' },
  { value: 'viewer', label: 'Наблюдатель' }
]

const form = ref({
  full_name: '',
  username: '',
  email: '',
  position: '',
  company: '',
  role: '',
  password: ''
})

onMounted(async () => {
  if (userId) {
    await fetchUser(userId)
    if (currentUser.value) {
      form.value = {
        full_name: currentUser.value.full_name || '',
        username: currentUser.value.username || '',
        email: currentUser.value.email || '',
        position: currentUser.value.position || '',
        company: currentUser.value.company || '',
        role: currentUser.value.role || '',
        password: ''
      }
    }
  }
})

const submitForm = async () => {
  isSubmitting.value = true

  const payload: UserUpdate = {
    email: form.value.email,
    username: form.value.username,
    role: form.value.role,
    full_name: form.value.full_name,
    position: form.value.position,
    company: form.value.company,
  }

  if (form.value.password.trim()) {
    payload.password = form.value.password
  }

  const updated = await updateUser(userId, payload)
  isSubmitting.value = false

  if (updated) {
    router.push(`/users/${userId}`)
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
  align-items: center;
  background: #ffffff;
  padding: 12px 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #0078d4;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}
.btn-back:hover { background-color: #f3f3f3; }

.page-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.form-card {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  padding: 24px;
  max-width: 700px;
}

.fluent-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-section-title {
  font-size: 13px;
  font-weight: 600;
  color: #0078d4;
  margin: 8px 0 4px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid #f3f2f1;
  padding-bottom: 6px;
}

.form-row {
  display: flex;
  gap: 16px;
}

@media (max-width: 600px) {
  .form-row { flex-direction: column; }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: #242424;
}

.fluent-input, .fluent-select {
  border: 1px solid #8a8886;
  border-bottom: 2px solid #605e5c;
  border-radius: 4px;
  height: 32px;
  padding: 0 10px;
  font-size: 13px;
  box-sizing: border-box;
  font-family: inherit;
  background: #ffffff;
  transition: border-color 0.15s ease;
  width: 100%;
}

.fluent-input:focus, .fluent-select:focus {
  outline: none;
  border-color: #0078d4;
  border-bottom-color: #0078d4;
  box-shadow: 0 0 0 1px #0078d4;
}

/* Элементы поля пароля */
.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input {
  padding-right: 36px;
}

.btn-toggle-password {
  position: absolute;
  right: 6px;
  background: transparent;
  border: none;
  color: #605e5c;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-toggle-password:hover {
  color: #242424;
  background-color: #f3f3f3;
}

.field-hint {
  font-size: 11px;
  color: #605e5c;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  border-top: 1px solid #f3f2f1;
  padding-top: 16px;
}

.btn-primary {
  background-color: #0078d4;
  color: #ffffff;
  border: none;
  height: 32px;
  padding: 0 20px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.btn-primary:hover { background-color: #106ebe; }
.btn-primary:disabled { background-color: #c8c8c8; cursor: not-allowed; }

.btn-secondary {
  background: #ffffff;
  border: 1px solid #d1d1d1;
  height: 32px;
  padding: 0 20px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  color: #242424;
  text-decoration: none;
  display: flex;
  align-items: center;
}
.btn-secondary:hover { background: #f5f5f5; }

.error-banner {
  background-color: #fde7e9;
  border-left: 4px solid #a80000;
  color: #a80000;
  padding: 10px 14px;
  border-radius: 4px;
  font-size: 13px;
}

.shimmer-loader {
  color: #605e5c;
  font-size: 13px;
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid #ffffff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>