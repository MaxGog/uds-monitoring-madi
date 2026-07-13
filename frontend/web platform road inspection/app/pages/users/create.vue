<template>
  <div class="monitoring-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <NuxtLink to="/users" class="btn-back" title="Назад к списку">⬅</NuxtLink>
        <h2 class="page-title">Добавление нового пользователя</h2>
      </div>
    </div>

    <div class="form-card">
      <form @submit.prevent="submitForm" class="fluent-form">
        <div v-if="error" class="error-banner">{{ error }}</div>

        <h3 class="form-section-title">Личные данные</h3>
        <div class="form-row">
          <div class="form-group">
            <label>ФИО сотрудника *</label>
            <input 
              v-model="form.full_name" 
              type="text" 
              class="fluent-input" 
              placeholder="Иванов Петр Сергеевич" 
              required 
            />
          </div>
          <div class="form-group">
            <label>Имя пользователя (Логин) *</label>
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
              placeholder="Главный специалист технадзора" 
            />
          </div>
          <div class="form-group">
            <label>Пароль *</label>
            <input 
              v-model="form.password" 
              type="password" 
              class="fluent-input" 
              placeholder="••••••••" 
              required 
            />
          </div>
        </div>

        <h3 class="form-section-title">Организация и Доступ</h3>
        <div class="form-row">
          <div class="form-group">
            <label>Компания / Организация *</label>
            <select v-model="form.company" class="fluent-select" required>
              <option v-for="comp in mockCompanies" :key="comp" :value="comp">{{ comp }}</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Роль в системе *</label>
            <select v-model="form.role" class="fluent-select" required>
              <option v-for="r in mockRoles" :key="r.value" :value="r.value">{{ r.label }}</option>
            </select>
          </div>
        </div>

        <div class="form-actions">
          <NuxtLink to="/users" class="btn-secondary">Отмена</NuxtLink>
          <button type="submit" class="btn-primary" :disabled="isLoading">
            {{ isLoading ? 'Сохранение...' : 'Создать пользователя' }}
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
  font-family: var(--fluent-font, sans-serif);
}

.toolbar {
  display: flex;
  align-items: center;
  background: #ffffff;
  padding: 16px 24px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-back {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #0078d4;
  text-decoration: none;
  padding: 4px 8px;
  border-radius: 4px;
}
.btn-back:hover { background-color: #f3f3f3; }

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #242424;
  margin: 0;
}

.form-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
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
  border-bottom: 1px solid #f3f3f3;
  padding-bottom: 4px;
}

.form-row {
  display: flex;
  gap: 20px;
}

@media (max-width: 600px) {
  .form-row { flex-direction: column; gap: 16px; }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: #242424;
}

.fluent-input, .fluent-select {
  border: 1px solid #a1a1a1;
  border-radius: 4px;
  height: 32px;
  padding: 0 10px;
  font-size: 13px;
  box-sizing: border-box;
  font-family: inherit;
  background: #ffffff;
}

.fluent-input:focus, .fluent-select:focus {
  outline: none;
  border-color: #0078d4;
  box-shadow: 0 0 0 1px #0078d4 inset;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  border-top: 1px solid #eaeaea;
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
}
.btn-primary:hover { background-color: #106ebe; }

.btn-secondary {
  background: #ffffff;
  border: 1px solid #e1e3e8;
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
.btn-secondary:hover { background: #f3f4f6; }
</style>