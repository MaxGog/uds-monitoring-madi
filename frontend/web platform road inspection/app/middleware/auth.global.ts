export default defineNuxtRouteMiddleware((to, from) => {
    const accessToken = useCookie('access_token')

    if (to.path === '/login/callback' || to.path === '/login') {
        return
    }

    if (!accessToken.value) {
        return navigateTo('/login')
    }
})