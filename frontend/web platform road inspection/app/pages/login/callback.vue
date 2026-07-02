<template>
  <div class="auth-card loading-card">
    <div class="fluent-spinner">
      <div class="spinner-circle"></div>
    </div>
    <h3 class="processing-title">Завершение авторизации</h3>
    <p class="processing-subtitle">Пожалуйста, подождите, проверяем параметры сессии...</p>

    <div v-if="authError" class="error-container">
      <p class="error-message">{{authError}}</p>
      <NuxtLink to="/login" class="btn-secondary error-retry-btn">Вернуться на страницу входа</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { handleCallback, authError, isLoading } = useAuth()


onMounted(async () => {
    await nextTick()
    const code = route.query.code as string
    if (code) {
        await handleCallback(code)
    } else {
        authError.value = 'Код авторизации не найден в ответе сервера'
    }
})
</script>

<style scoped>

.loading-card {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.processing-title {
  font-size: 16px;
  font-weight: 600;
  color: #323130;
  margin: 16px 0 4px 0;
}

.processing-subtitle {
  font-size: 13px;
  color: #605e5c;
  margin-bottom: 20px;
}

.fluent-spinner {
  width: 32px;
  height: 32px;
  position: relative;
}

.spinner-circle {
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  border: 2.5px solid #eaeaea;
  border-top-color: var(--fluent-blue, #0078d4);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  margin-top: 15px;
  width: 100%;
}

.error-message {
  padding: 10px;
  background-color: #fde7e9;
  border-radius: 4px;
  color: #a80000;
  font-size: 13px;
  text-align: left;
  margin-bottom: 12px;
}

.error-retry-btn {
  text-decoration: none;
  font-size: 13px;
}
</style>