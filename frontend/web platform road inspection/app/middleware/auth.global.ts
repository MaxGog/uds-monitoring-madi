export default defineNuxtRouteMiddleware(async (to, from) => {
  if (to.path === "/login/callback" || to.path === "/login") {
    return;
  }

  const accessToken = useState("access_token");

  if (!accessToken.value) {
    try {
      const { access } = await $fetch<{ access: string }>(
        `http://localhost:8000/auth/refresh`,
        {
            method: "POST"
        },
      );
      accessToken.value = access;
    } catch (e) {
      return navigateTo("/login");
    }
  }
});
