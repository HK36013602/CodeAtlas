import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
export default defineConfig({plugins:[vue()],server:{port:5273,proxy:{'/api':'http://localhost:8100'}},build:{rollupOptions:{output:{manualChunks:{vue:['vue'],charts:['echarts']}}}}});
