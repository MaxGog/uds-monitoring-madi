<template>
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
</script>