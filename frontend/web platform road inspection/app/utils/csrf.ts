export default defineNuxtPlugin(async () => {
  const csrfCookie = useCookie('fastapi-csrf-token')

  if (!csrfCookie.value) {
    try {
      await $fetch('http://localhost:8000/auth/csrf', { credentials: 'include' })
    } catch (err) {
      console.log('Не удалось получить CSRF токен', err)
    }
  }
})