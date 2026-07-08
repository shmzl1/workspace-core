import { createApp } from 'vue';
import App from './App.vue';
import router from './app/router';
import { setupGuards } from './app/router/guards';
import './shared/styles/global.scss';
import './index.css';

const app = createApp(App);

setupGuards(router);
app.use(router);
app.mount('#app');
