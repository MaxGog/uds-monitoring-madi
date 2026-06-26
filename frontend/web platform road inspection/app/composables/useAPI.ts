export const apiFetch = $fetch.create({
  baseURL: 'http://127.0.0.1:8000',
onRequest({ options }) {
    const headers = new Headers(options.headers)

    const accessToken = useCookie('access_token').value
    if (accessToken) {
      headers.set('Authorization', `Bearer ${accessToken}`)
    }

    if (options.method && options.method !== 'GET') {
      const csrfToken = useCookie('fastapi-csrf-token').value
      if (csrfToken) {
        headers.set('X-CSRF-Token', csrfToken)
      }
    }
    options.headers = headers
  },
  onResponseError({ response }) {
    if (response.status === 401) {
      // Логика logout / редиректа при протухании токена
    }
  },
})