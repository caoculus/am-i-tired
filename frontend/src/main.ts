import './style.css'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config'
import Lara from './presets/lara'

const app = createApp(App)

app.use(router)
app.use(PrimeVue, {
  unstyled: true,
  pt: Lara
})
app.mount('#app')
