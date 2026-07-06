import { apiFetch } from '~/composables/useAPI'
import { generateCodeVerifier, generateCodeChallenge } from '~/utils/pkce'

interface TokenResponse {
  access_token: string
  refresh_token: string
  user: { id: number; email: string; role: string }
}

interface UserInfo {
  id: number
  email: string
  role: string
  name?: string
}

export function useAuth() {
  const accessToken = useState<string | null>('access_token', () => null)
  const user = useState<UserInfo | null>('auth_user', () => null)
  const isLoading = ref(false)
  const authError = ref<string | null>(null)
  const config = useRuntimeConfig()
  const mockAuthEnabled = config.public.mockAuthEnabled
  const redirectUri = 'http://localhost:4000/login/callback' // Редирект для коллбэка

  const accessCookie = useCookie('access_token')
  const mockUserStorageKey = 'mock_auth_user'

  const restoreMockUser = () => {
    if (!process.client || !mockAuthEnabled) {
      return
    }

    const saved = localStorage.getItem(mockUserStorageKey)
    if (saved) {
      try {
        user.value = JSON.parse(saved)
      } catch (e) {
        console.warn('Не удалось восстановить mock-пользователя из localStorage', e)
      }
    }
  }

  if (process.client) {
    restoreMockUser()
  }

  const loginWithPKCE = async () => {
    isLoading.value = true
    try {
      const verifier = generateCodeVerifier()
      const challenge = await generateCodeChallenge(verifier)

      sessionStorage.setItem('pkce_code_verifier', verifier)

      const authUrl = new URL('http://localhost:8000/auth/authorize')
      authUrl.searchParams.append('response_type', 'code')
      authUrl.searchParams.append('client_id', 'web-platform-madi')
      authUrl.searchParams.append('redirect_uri', redirectUri)
      authUrl.searchParams.append('code_challenge', challenge)
      authUrl.searchParams.append('code_challenge_method', 'S256')

      window.location.href = authUrl.toString()
    } catch (err) {
      authError.value = 'Ошибка инициализации PKCE'
      isLoading.value = false
    }
  }

  const handleCallback = async (code: string) => {
    console.log('Handle Callback')
    isLoading.value = true
    authError.value = null

    const verifier = sessionStorage.getItem('pkce_code_verifier')
    if (!verifier) {
      console.log('Сессия PKCE истекла или неверна')
      authError.value = 'Сессия PKCE истекла или неверна'
      isLoading.value = false
      return
    }

    try {
      const formData = new URLSearchParams()
      formData.append('grant_type', 'authorization_code')
      formData.append('code', code)
      formData.append('redirect_uri', redirectUri)
      formData.append('client_id', 'web-platform-madi')
      formData.append('code_verifier', verifier)

      const response = await apiFetch<TokenResponse>('/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
      })

      accessToken.value = response.access_token
      user.value = response.user
      accessCookie.value = response.access_token
      sessionStorage.removeItem('pkce_code_verifier')
      localStorage.removeItem(mockUserStorageKey)

      await navigateTo('/')
    } catch (err: any) {
      console.error('Ошибка при обмене токена:', err)
      authError.value = err.data?.detail || 'Не удалось подтвердить код авторизации'
    } finally {
      isLoading.value = false
    }
  }

  const loginMockUser = () => {
    if (!mockAuthEnabled) {
      return
    }

    const mockToken = 'mock-developer-token'
    const mockUser: UserInfo = {
      id: 0,
      email: 'dev@madi.ru',
      role: 'Администратор',
      name: 'Разработчик'
    }

    accessToken.value = mockToken
    accessCookie.value = mockToken
    user.value = mockUser

    if (process.client) {
      localStorage.setItem(mockUserStorageKey, JSON.stringify(mockUser))
    }

    navigateTo('/')
  }

  return {
    isLoading,
    authError,
    loginWithPKCE,
    handleCallback,
    loginMockUser,
    user
  }
}
