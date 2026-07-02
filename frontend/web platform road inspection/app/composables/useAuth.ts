import { apiFetch } from '~/composables/useAPI'
import { generateCodeVerifier, generateCodeChallenge } from '~/utils/pkce'

interface TokenResponse {
  access_token: string
  refresh_token: string
  user: { id: number; email: string; role: string }
}

export function useAuth() {
  const accessToken = useCookie<string | null>('access_token', { default: () => null })
  const refreshToken = useCookie<string | null>('refresh_token', { default: () => null })
  const user = useState('auth_user', () => null)
  
  const isLoading = ref(false)
  const authError = ref<string | null>(null)

  const config = useRuntimeConfig()
  const redirectUri = 'http://localhost:4000/login/callback' // Редирект для коллбэка

  // Шаг 1: Инициализация PKCE и редирект на форму авторизации
  const loginWithPKCE = async () => {
    isLoading.value = true
    try {
      const verifier = generateCodeVerifier()
      const challenge = await generateCodeChallenge(verifier)

      // Сохраняем verifier локально в sessionStorage на время редиректа
      sessionStorage.setItem('pkce_code_verifier', verifier)

      // URL для эндпоинта авторизации FastAPI
      const authUrl = new URL('http://localhost:8000/auth/authorize')
      authUrl.searchParams.append('response_type', 'code')
      authUrl.searchParams.append('client_id', 'web-platform-madi')
      authUrl.searchParams.append('redirect_uri', redirectUri)
      authUrl.searchParams.append('code_challenge', challenge)
      authUrl.searchParams.append('code_challenge_method', 'S256')

      // Уходим на страницу авторизации бэкенда
      window.location.href = authUrl.toString()
    } catch (err) {
      authError.value = 'Ошибка инициализации PKCE'
      isLoading.value = false
    }
  }

  // Шаг 2: Обмен полученного Authorization Code + Verifier на токены
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
      console.log(response)

      accessToken.value = response.access_token
      refreshToken.value = response.refresh_token
      user.value = response.user

      sessionStorage.removeItem('pkce_code_verifier')
      
      await navigateTo('/')
    } catch (err: any) {
      console.error('Ошибка при обмене токена:', err)
      authError.value = err.data?.detail || 'Не удалось подтвердить код авторизации'
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    authError,
    loginWithPKCE,
    handleCallback
  }
}