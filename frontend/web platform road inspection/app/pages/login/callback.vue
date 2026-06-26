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

<template>
  <div class="callback-container">
    <div v-if="isLoading" class="loader">
      <p>Авторизация, пожалуйста подождите...</p>
    </div>
    
    <div v-if="authError" class="error-card">
      <h3>Ошибка авторизации</h3>
      <p>{{ authError }}</p>
      <NuxtLink to="/login" class="btn-retry">Вернуться на страницу входа</NuxtLink>
    </div>
  </div>
</template>