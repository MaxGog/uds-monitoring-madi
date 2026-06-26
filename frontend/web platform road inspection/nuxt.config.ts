// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  css: [
    '~/assets/css/global.css',
  ],
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  devServer: {
    port: 4000,
    host: "http://127.0.0.1/",
  },

  modules: [
    //'@pinia/nuxt',
    //'nuxt-auth-utils',
  ],
})