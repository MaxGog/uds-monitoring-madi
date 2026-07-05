const BACKEND_URL = "http://localhost:8000";
let refreshPromise: Promise<string | null> | null = null;

export const apiFetch = $fetch.create({
  baseURL: BACKEND_URL,
  credentials: "include",

  async onRequest({ options }) {
    const headers = new Headers(options.headers);

    const accessToken = useState("access_token").value;
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
    console.log("Поймали ошибку:", response.status);
    const accessToken = useState("access_token");

    if (response.status === 401 && !request.toString().includes("/auth/refresh")) {
      console.log("Это 401, пробуем обновить...");
      if (!refreshPromise) {
        refreshPromise = (async () => {
      try {
        const newTokens = await $fetch<{ access_token: string }>(`${BACKEND_URL}/auth/refresh`, {
          method: "POST",
          credentials: 'include',
          headers: {
            "Authorization": `Bearer ${accessToken.value}`
          },
        });

        accessToken.value = newTokens.access_token;
        // Повторяем исходный запрос
        options.headers = new Headers(options.headers);
        options.headers.set("Authorization", `Bearer ${newTokens.access_token}`);
        return $fetch(request, options);
      } catch (refreshError) {
        console.log('Refresh токен протух или отсутствует, выкидываем на логин');
        const accessToken = useState("access_token");
        accessToken.value = null;
        return navigateTo("/login");
      } finally {
        refreshPromise = null;
      }
    })()
  }
    } else {
      // Нет токена — редирект на логин
      navigateTo("/login");
    }
  },
});
