export default defineNuxtRouteMiddleware(async (to, from) => {
  if (to.path === "/login/callback" || to.path === "/login") {
    return;
  }

  const accessToken = useState("access_token")
  const cookieToken = useCookie("access_token").value

  if (!accessToken.value && cookieToken) {
    accessToken.value = cookieToken as string
  }

  const config = useRuntimeConfig()
  const mockAuthEnabled = config.public.mockAuthEnabled
  const userState = useState('auth_user')

  if (mockAuthEnabled && !userState.value && process.client) {
    const saved = localStorage.getItem('mock_auth_user')
    if (saved) {
      try {
        userState.value = JSON.parse(saved)
      } catch {
        localStorage.removeItem('mock_auth_user')
      }
    }
  }

  if (!accessToken.value) {
    try {
      const { access } = await $fetch<{ access: string }>(
        `http://localhost:8000/auth/refresh`,
        {
          method: "POST"
        },
      )
      accessToken.value = access
    } catch (e) {
      return navigateTo("/login")
    }
  }
});
