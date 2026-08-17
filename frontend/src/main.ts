import { createApp } from 'vue';
import '@fontsource-variable/manrope';
import '@fontsource/jetbrains-mono/400.css';
import './styles.css';
import App from './App.vue';
import { router } from './router';
const legacy=window.location.hash.slice(1);if(window.location.pathname==='/'&&['map','risks','files','repository'].includes(legacy))window.history.replaceState(null,'',`/${legacy}`)
createApp(App).use(router).mount('#app');
