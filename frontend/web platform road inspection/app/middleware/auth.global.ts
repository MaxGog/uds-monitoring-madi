export default defineNuxtRouteMiddleware((to, from) => {
    const authToken = useCookie('auth_token')

    if (to.path === '/login') {
        return
    }

    if (!authToken.value) {
        return navigateTo('/login')
    }
})