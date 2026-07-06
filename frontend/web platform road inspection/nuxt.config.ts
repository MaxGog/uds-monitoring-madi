// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  css: ["~/assets/css/global.css"],
  compatibilityDate: "2025-07-15",
  runtimeConfig: {
    public: {
      mockAuthEnabled: process.env.NUXT_PUBLIC_MOCK_AUTH === 'true'
    }
  },
  devtools: { enabled: true },
  devServer: {
    port: 4000,
    host: "http://localhost/",
  },
});
