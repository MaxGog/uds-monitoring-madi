<template>
  <div class="monitoring-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <NuxtLink to="/users" class="btn-back" title="Назад к списку">
          <svg class="icon-back" viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
            <path d="M10.354 3.646a.5.5 0 0 1 0 .708L6.207 8.5l4.147 4.146a.5.5 0 0 1-.708.708l-4.5-4.5a.5.5 0 0 1 0-.708l4.5-4.5a.5.5 0 0 1 .708 0z"/>
          </svg>
           Назад
        </NuxtLink>
        <h2 class="page-title">Добавление нового пользователя</h2>
      </div>
    </div>

    <div class="form-card">
      <form @submit.prevent="submitForm" class="fluent-form">
        <!-- Fluent MessageBar error indicator -->
        <div v-if="error" class="error-banner" role="alert">
          <svg class="error-icon" viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
            <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995z"/>
          </svg>
          <span>{{ error }}</span>
        </div>

        <div class="form-section">
          <h3 class="form-section-title">Личные данные</h3>
          <div class="form-row">
            <div class="form-group">
              <label for="fullName">ФИО сотрудника <span class="required-star">*</span></label>
              <input 
                id="fullName"
                v-model="form.full_name" 
                type="text" 
                class="fluent-input" 
                placeholder="Иванов Петр Сергеевич" 
                required 
              />
            </div>
            <div class="form-group">
              <label for="username">Имя пользователя (Логин) <span class="required-star">*</span></label>
              <input 
                id="username"
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
              <label for="email">Рабочий Email <span class="required-star">*</span></label>
              <input 
                id="email"
                v-model="form.email" 
                @input="handleEmailInput"
                type="email" 
                class="fluent-input" 
                placeholder="p.ivanov@company.ru" 
                required 
              />
            </div>
            <div class="form-group">
              <label for="position">Должность</label>
              <input 
                id="position"
                v-model="form.position" 
                type="text" 
                class="fluent-input" 
                placeholder="Главный специалист технадзора" 
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="password">Пароль <span class="required-star">*</span></label>
              <div class="password-wrapper">
                <input 
                  id="password"
                  v-model="form.password" 
                  :type="showPassword ? 'text' : 'password'" 
                  class="fluent-input password-input" 
                  placeholder="••••••••" 
                  required 
                />
                <button 
                  type="button" 
                  class="password-toggle" 
                  @click="showPassword = !showPassword"
                  :title="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
                >
                  <svg v-if="!showPassword" viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
                    <path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/>
                    <path d="M0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8zm8 3.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z"/>
                  </svg>
                  <svg v-else viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
                    <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>
                    <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>
                    <path d="M3.35 5.47c-.18.158-.353.321-.518.486A13.134 13.134 0 0 0 1.172 8c.058.087.122.183.195.288.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.707z"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="form-section">
          <h3 class="form-section-title">Организация и Доступ</h3>
          <div class="form-row">
            <div class="form-group">
              <label for="company">Компания / Организация <span class="required-star">*</span></label>
              <select id="company" v-model="form.company" class="fluent-select" required>
                <option v-for="comp in mockCompanies" :key="comp" :value="comp">{{ comp }}</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="role">Роль в системе <span class="required-star">*</span></label>
              <select id="role" v-model="form.role" class="fluent-select" required>
                <option v-for="r in mockRoles" :key="r.value" :value="r.value">{{ r.label }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <NuxtLink to="/users" class="btn-secondary">Отмена</NuxtLink>
          <button type="submit" class="btn-primary" :disabled="isLoading">
            <span v-if="isLoading" class="spinner"></span>
            <span>{{ isLoading ? 'Сохранение...' : 'Создать пользователя' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUser } from '~/composables/useUser'
import type { UserCreate } from '~/types/user'

const router = useRouter()
const { createUser, isLoading, error } = useUser()

const showPassword = ref(false)

const mockCompanies = [
  'ООО "ТехноМониторинг"',
  'АО "СтройКонтроль"',
  'ГБУ "Автодор-МАДИ"'
]

const mockRoles = [
  { value: 'admin', label: 'Администратор' },
  { value: 'engineer', label: 'Инженер технадзора' },
  { value: 'viewer', label: 'Наблюдатель' }
]

const form = ref({
  full_name: '',
  username: '',
  email: '',
  position: '',
  company: mockCompanies[0],
  role: 'engineer',
  password: ''
})

const handleEmailInput = () => {
  if (!form.value.username && form.value.email.includes('@')) {
    form.value.username = form.value.email.split('@')[0]
  }
}

const submitForm = async () => {
  const payload: UserCreate = {
    full_name: form.value.full_name,
    username: form.value.username || form.value.email.split('@')[0],
    email: form.value.email,
    position: form.value.position,
    company: form.value.company,
    role: form.value.role,
    password: form.value.password
  }

  const created = await createUser(payload)
  if (created) {
    router.push('/users')
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
  gap: 12px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  color: #0078d4;
  text-decoration: none;
  padding: 6px 10px;
  border-radius: 4px;
  transition: background-color 0.1s ease;
}
.btn-back:hover { background-color: #f3f3f3; }
.btn-back:active { background-color: #edebe9; }

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #242424;
  margin: 0;
}

.form-card {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 24px;
  max-width: 680px;
}

.fluent-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-section-title {
  font-size: 12px;
  font-weight: 700;
  color: #0078d4;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  border-bottom: 1px solid #f3f2f1;
  padding-bottom: 6px;
}

.form-row {
  display: flex;
  gap: 16px;
}

@media (max-width: 600px) {
  .form-row { flex-direction: column; gap: 12px; }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #323130;
}

.required-star {
  color: #a80000;
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
  color: #242424;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.fluent-input:hover, .fluent-select:hover {
  border-color: #323130;
}

.fluent-input:focus, .fluent-select:focus {
  outline: none;
  border-color: #0078d4;
  border-bottom-color: #0078d4;
  box-shadow: 0 0 0 1px #0078d4;
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input {
  width: 100%;
  padding-right: 32px;
}

.password-toggle {
  position: absolute;
  right: 6px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #605e5c;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 2px;
}

.password-toggle:hover {
  color: #242424;
  background-color: #f3f3f3;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #fde7e9;
  border-left: 4px solid #a80000;
  color: #a80000;
  padding: 10px 14px;
  border-radius: 4px;
  font-size: 13px;
}

.error-icon {
  flex-shrink: 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
  border-top: 1px solid #edebe9;
  padding-top: 16px;
}

.btn-primary {
  background-color: #0078d4;
  color: #ffffff;
  border: 1px solid transparent;
  height: 32px;
  padding: 0 20px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.1s ease;
}

.btn-primary:hover:not(:disabled) { background-color: #106ebe; }
.btn-primary:active:not(:disabled) { background-color: #005a9e; }
.btn-primary:disabled {
  background-color: #f3f2f1;
  color: #a19f9d;
  cursor: not-allowed;
}

.btn-secondary {
  background: #ffffff;
  border: 1px solid #8a8886;
  height: 32px;
  padding: 0 20px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  color: #242424;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  transition: background-color 0.1s ease, border-color 0.1s ease;
}

.btn-secondary:hover { 
  background: #f3f3f3; 
  border-color: #323130;
}
.btn-secondary:active { background: #edebe9; }

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