// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  
  devtools: { enabled: true },
  
  modules: ['@nuxtjs/tailwindcss'],
  
  typescript: {
    strict: true,
    typeCheck: false,
  },
  
  runtimeConfig: {
    public: {
      backendUrl: process.env.BACKEND_URL || 'http://localhost:8000',
    },
  },
  
  app: {
    head: {
      title: '身分證資訊擷取系統',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '使用 AI 自動辨識身分證資訊' },
      ],
    },
  },
})
