// frontend/vite.config.ts
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const HOST = env.VITE_API_HOST || "localhost";

  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: true,
      proxy: {
        // ───────────────────── Auth (8000)
        "/api/v1/auth": { target: `http://${HOST}:8000`, changeOrigin: true, secure: false },
        "/api/v1/users": { target: `http://${HOST}:8000`, changeOrigin: true, secure: false },
        "/api/v1/roles": { target: `http://${HOST}:8000`, changeOrigin: true, secure: false },

        // ───────────────────── CRM (8001)
        "/api/v1/customers": { target: `http://${HOST}:8001`, changeOrigin: true, secure: false },
        "/api/v1/interactions": { target: `http://${HOST}:8001`, changeOrigin: true, secure: false },
        "/api/v1/feedback": { target: `http://${HOST}:8001`, changeOrigin: true, secure: false },
        "/api/v1/segments": { target: `http://${HOST}:8001`, changeOrigin: true, secure: false },

        // ───────────────────── Booking (8002)
        "/api/v1/bookings": { target: `http://${HOST}:8002`, changeOrigin: true, secure: false },
        "/api/v1/reservations": { target: `http://${HOST}:8002`, changeOrigin: true, secure: false },
        "/api/v1/availability": { target: `http://${HOST}:8002`, changeOrigin: true, secure: false },
        "/api/v1/pricing": { target: `http://${HOST}:8002`, changeOrigin: true, secure: false },

        // ───────────────────── Driver (8003)
        "/api/v1/drivers": { target: `http://${HOST}:8003`, changeOrigin: true, secure: false },
        "/api/v1/incidents": { target: `http://${HOST}:8003`, changeOrigin: true, secure: false },
        "/api/v1/training": { target: `http://${HOST}:8003`, changeOrigin: true, secure: false },

        // ───────────────────── Fleet (8004)
        // FIX: assignments belong to Fleet, not Driver
        "/api/v1/assignments": { target: `http://${HOST}:8004`, changeOrigin: true, secure: false },
        "/api/v1/vehicles": { target: `http://${HOST}:8004`, changeOrigin: true, secure: false },
        "/api/v1/maintenance": { target: `http://${HOST}:8004`, changeOrigin: true, secure: false },
        // NEW: used by the fleet dashboard
        "/api/v1/documents": { target: `http://${HOST}:8004`, changeOrigin: true, secure: false },
        "/api/v1/fuel": { target: `http://${HOST}:8004`, changeOrigin: true, secure: false },
        // Optional catch-all if your backend mounts as /api/v1/fleet/*
        "/api/v1/fleet": { target: `http://${HOST}:8004`, changeOrigin: true, secure: false },

        // ───────────────────── Financial (8005)
        "/api/v1/invoices": { target: `http://${HOST}:8005`, changeOrigin: true, secure: false },
        "/api/v1/payments": { target: `http://${HOST}:8005`, changeOrigin: true, secure: false },
        "/api/v1/expenses": { target: `http://${HOST}:8005`, changeOrigin: true, secure: false },
        "/api/v1/analytics": { target: `http://${HOST}:8005`, changeOrigin: true, secure: false },

        // ───────────────────── HR (8006)
        "/api/v1/employees": { target: `http://${HOST}:8006`, changeOrigin: true, secure: false },
        "/api/v1/schedules": { target: `http://${HOST}:8006`, changeOrigin: true, secure: false },
        "/api/v1/payroll": { target: `http://${HOST}:8006`, changeOrigin: true, secure: false },

        // ───────────────────── Inventory (8007)
        "/api/v1/inventory": { target: `http://${HOST}:8007`, changeOrigin: true, secure: false },
        "/api/v1/parts": { target: `http://${HOST}:8007`, changeOrigin: true, secure: false },
        "/api/v1/suppliers": { target: `http://${HOST}:8007`, changeOrigin: true, secure: false },

        // ───────────────────── Notification (8008)
        "/api/v1/notifications": { target: `http://${HOST}:8008`, changeOrigin: true, secure: false },
        "/api/v1/templates": { target: `http://${HOST}:8008`, changeOrigin: true, secure: false },

        // ───────────────────── QA (8009)
        "/api/v1/quality": { target: `http://${HOST}:8009`, changeOrigin: true, secure: false },
        "/api/v1/audits": { target: `http://${HOST}:8009`, changeOrigin: true, secure: false },
        "/api/v1/reports": { target: `http://${HOST}:8009`, changeOrigin: true, secure: false },

        // ───────────────────── Tour (8010)
        "/api/v1/tours": { target: `http://${HOST}:8010`, changeOrigin: true, secure: false },
        "/api/v1/packages": { target: `http://${HOST}:8010`, changeOrigin: true, secure: false },
        "/api/v1/guides": { target: `http://${HOST}:8010`, changeOrigin: true, secure: false },
        "/api/v1/incidents": { target: `http://${HOST}:8010`, changeOrigin: true, secure: false },
        "/api/v1/tour-templates": { target: `http://${HOST}:8010`, changeOrigin: true, secure: false },
        "/api/v1/tour-instances": { target: `http://${HOST}:8010`, changeOrigin: true, secure: false },
        "/api/v1/itinerary": { target: `http://${HOST}:8010`, changeOrigin: true, secure: false },

        // ───────────────────── Keep LAST — fallback to Auth
        "/api/v1": { target: `http://${HOST}:8000`, changeOrigin: true, secure: false },
      },
    },
    optimizeDeps: { exclude: ["lucide-react"] },
  };
});
