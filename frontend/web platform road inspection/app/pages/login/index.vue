<!-- <template>
  <div class="auth-card">
    <h2 class="auth-title">Вход в систему</h2>
    <p class="auth-subtitle">Мониторинг состояния объектов УДС</p>

    <form @submit.prevent="handleSubmit" class="auth-form">
      <div class="input-group">
        <label for="email">Электронная почта</label>
        <input 
          id="email" 
          v-model="form.email" 
          type="email" 
          placeholder="name@example.com" 
          required 
        />
      </div>

      <div class="input-group">
        <label for="password">Пароль</label>
        <input 
          id="password" 
          v-model="form.password" 
          type="password" 
          placeholder="••••••••" 
          required 
        />
      </div>

      <button type="submit" class="btn-primary">Войти</button>
    </form>

    <div class="fluent-divider">
      <span>или</span>
    </div>

    <button type="button" class="btn-secondary dev-btn" @click="handleDevLogin">
      <span class="dev-icon">⚡</span> Войти как разработчик
    </button>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'

definePageMeta({
  layout: 'auth' as any
})

const router = useRouter()
const authToken = useCookie('auth_token')

const form = reactive({
  email: '',
  password: ''
})

const handleSubmit = () => {
  authToken.value = 'fake-jwt-token-from-server'
  console.log('Авторизация успешна:', form.email)
  router.push('/')
}

const handleDevLogin = () => {
  authToken.value = 'developer-bypass-token'
  console.log('Вход в режиме разработчика...')
  router.push('/')
}
</script> -->

<script setup lang="ts">
const { loginWithPKCE, isLoading, authError } = useAuth()
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h2>Вход в систему</h2>
      <p class="subtitle">MADI Infrastructure Platform</p>

      <button @click="loginWithPKCE" :disabled="isLoading" class="btn-submit">
        {{ isLoading ? 'Перенаправление...' : 'Войти через Единую Систему' }}
      </button>

      <p v-if="authError" class="error-message">{{ authError }}</p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fb;
  font-family: system-ui, -apple-system, sans-serif;
}

.login-card {
  background: #ffffff;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 400px;
}

h2 {
  margin: 0 0 0.5rem 0;
  color: #1e293b;
  font-size: 1.75rem;
  text-align: center;
}

.subtitle {
  margin: 0 0 2rem 0;
  color: #64748b;
  font-size: 0.875rem;
  text-align: center;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #334155;
}

input {
  padding: 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus {
  outline: none;
  border-color: #3b82f6;
}

input:disabled {
  background-color: #f8fafc;
  cursor: not-allowed;
}

.error-message {
  background-color: #fef2f2;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  border: 1px solid #fee2e2;
}

.btn-submit {
  background-color: #2563eb;
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 0.5rem;
}

.btn-submit:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.btn-submit:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}
</style>