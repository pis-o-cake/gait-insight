import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      // 개발 중에는 화면과 API 주소를 하나로 맞춘다. 로그인 쿠키가 그대로 오간다.
      "/api": { target: "http://localhost:8000", changeOrigin: false },
    },
  },
  build: { outDir: "dist", assetsDir: "assets", sourcemap: false },
});
