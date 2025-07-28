import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  /**
   * When your browser calls http://localhost:5173/api/v1/…
   * Vite will forward the request to the backend (or gateway)
   * and return the JSON.  No more index.html fall-back.
   */
  server: {
    proxy: {
      // Everything under /api/v1 goes to the compose service “auth_service”
      // (replace with gateway if you have one).
      "/api/v1": {
        target: "http://localhost:8000",  // <-  FastAPI in dev
        changeOrigin: true,
        secure: false,
      },
    },
  },
  optimizeDeps: { exclude: ["lucide-react"] },
});
