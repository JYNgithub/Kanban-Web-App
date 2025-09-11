import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'

// Create a simple router view component
const RouterApp = {
  template: '<router-view />'
}

const app = createApp(RouterApp)
app.use(createPinia())
app.use(router)
app.mount('#app')