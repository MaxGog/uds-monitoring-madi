// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  css: ["~/assets/css/global.css"],
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  devServer: {
    port: 4000,
    host: "http://localhost/",
  },
});
