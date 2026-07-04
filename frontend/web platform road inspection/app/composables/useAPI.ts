export const apiFetch = $fetch.create({
  baseURL: "http://127.0.0.1:8000",
  async onRequest({ options }) {
    const headers = new Headers(options.headers);

    const accessToken = useCookie("access_token").value;
    if (accessToken) {
      headers.set("Authorization", `Bearer ${accessToken}`);
    }

    if (options.method && options.method !== "GET") {
      const csrfToken = useCookie("fastapi-csrf-token").value;
      if (csrfToken) {
        headers.set("X-CSRF-Token", csrfToken);
      }
    }
    options.headers = headers;
  },
  async onResponseError({ request, response, options }) {
    console.log('Поймали ошибку:', response.status);
    if (response.status === 401 && !request.toString().includes('/auth/refresh')) {
      console.log('Это 401, пробуем обновить...');
      const accessToken = useCookie("access_token");
      const refreshToken = useCookie("refresh_token");

      if (refreshToken.value) {
        try {
          const newTokens = await $fetch<{ access: string }>(
            "http://127.0.0.1:8000/auth/refresh",
            {
              method: "POST",
              body: {
                access_token: accessToken.value,
                refresh_token: refreshToken.value 
              },
            },
          );

          accessToken.value = newTokens.access;
          // Повторяем исходный запрос
          options.headers = new Headers(options.headers);
          options.headers.set("Authorization", `Bearer ${newTokens.access}`);
          return $fetch(request);
        } catch (refreshError) {
          // Если refresh токен тоже протух — логаут
          accessToken.value = null;
          refreshToken.value = null;
          navigateTo("/login");
        }
      } else {
        // Нет токена — редирект на логин
        navigateTo("/login");
      }
    }
  },
});
