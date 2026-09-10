<template>
  <div class="auth-card">
    <h2 class="auth-title">Авторизация</h2>
    <p class="auth-subtitle">Система мониторинга состояния объектов УДС</p>

    <div class="auth-form">
      <button 
        class="btn-primary" 
        :disabled="isLoading" 
        @click="handleLogin"
      >
        <span v-if="isLoading">Инициализация входа...</span>
        <span v-else>Войти через Единую Учетную Запись</span>
      </button>

      <div v-if="authError" class="error-message">
        {{ authError }}
      </div>

      <div v-if="mockAuthEnabled">
        <div class="fluent-divider">Или войти как разработчик</div>

        <button 
          class="btn-secondary dev-btn" 
          @click="loginAsDeveloper"
          type="button"
        >
          <span class="dev-icon">⚙️</span> Локальный вход (Bypass)
        </button>
      </div>

      <div v-else class="mock-disabled-note">
        Локальный вход отключён. Включите `NUXT_PUBLIC_MOCK_AUTH=true` для тестирования без бэкенда.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

// Указываем Nuxt использовать лэйаут для авторизации
definePageMeta({
  layout: 'auth'
})

const { loginWithPKCE, loginMockUser, isLoading, authError } = useAuth()
const config = useRuntimeConfig()
const mockAuthEnabled = config.public.mockAuthEnabled

const handleLogin = async () => {
  await loginWithPKCE()
}

const loginAsDeveloper = async () => {
  if (!mockAuthEnabled) {
    return
  }
  await loginMockUser()
}
</script>


<style scoped>
.auth-card {
    margin: auto;
    position: relative;
    z-index: 2;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--fluent-gray-40, #e1e3e8);
    border-radius: 8px;
    padding: 36px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), 0 1px 4px rgba(0, 0, 0, 0.04);
}

.auth-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--fluent-gray-100, #323742);
    margin-bottom: 4px;
    margin-top: 0;
}

.auth-subtitle {
    font-size: 13px;
    color: var(--fluent-gray-60, #a0a6b3);
    margin-bottom: 28px;
}

.auth-form {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.input-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.input-group label {
    font-size: 12px;
    font-weight: 600;
    color: var(--fluent-gray-100, #323742);
}

.input-group input {
    height: 32px;
    padding: 0 10px;
    font-size: 14px;
    background: #ffffff;
    border: 1px solid var(--fluent-gray-40, #e1e3e8);
    border-bottom: 1px solid var(--fluent-gray-60, #a0a6b3);
    border-radius: 4px;
    outline: none;
    transition: all 0.1s ease;
}

.input-group input:hover {
    background-color: #f9f9f9;
    border-color: var(--fluent-gray-60, #a0a6b3);
}

.input-group input:focus {
    background: #ffffff;
    border-color: transparent;
    box-shadow:
        0 0 0 1px var(--fluent-blue, #0078d4) inset,
        0 -2px 0 0 var(--fluent-blue, #0078d4) inset;
}

.btn-primary,
.btn-secondary {
    height: 32px;
    font-size: 14px;
    font-weight: 600;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.1s ease;
}

.btn-primary {
    background-color: var(--fluent-blue, #0078d4);
    color: #ffffff;
    border: 1px solid transparent;
    box-shadow: 0 2px 4px rgba(0, 120, 212, 0.2);
}

.btn-primary:hover {
    background-color: #106ebe;
}

.btn-primary:active {
    background-color: #005a9e;
}

.btn-secondary {
    background-color: #ffffff;
    color: var(--fluent-gray-100, #323742);
    border: 1px solid var(--fluent-gray-40, #e1e3e8);
}

.btn-secondary:hover {
    background-color: #f3f4f6;
    border-color: var(--fluent-gray-60, #a0a6b3);
}

.fluent-divider {
    display: flex;
    align-items: center;
    text-align: center;
    margin: 20px 0;
    color: var(--fluent-gray-60, #a0a6b3);
    font-size: 12px;
}

.fluent-divider::before,
.fluent-divider::after {
    content: '';
    flex: 1;
    border-bottom: 1px solid var(--fluent-gray-40, #e1e3e8);
}

.fluent-divider:not(:empty)::before {
    margin-right: .5em;
}

.fluent-divider:not(:empty)::after {
    margin-left: .5em;
}

.dev-btn {
    width: 100%;
    gap: 8px;
    border-style: dashed;
}

.dev-icon {
    font-size: 14px;
}

.error-message {
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #fde7e9;
  border-left: 3px solid #d13438;
  color: #a80000;
  font-size: 13px;
  border-radius: 4px;
}
</style>