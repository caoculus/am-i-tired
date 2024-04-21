import './style.css'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config'
import Lara from './presets/lara'
import Ripple from 'primevue/ripple'
import ToastService from 'primevue/toastservice'

const app = createApp(App)

app.use(router)
app.use(PrimeVue, {
  unstyled: true,
  pt: Lara,
  ripple: true,
})
app.use(ToastService)
app.directive('ripple', Ripple)
app.mount('#app')
