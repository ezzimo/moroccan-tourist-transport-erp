import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  /**
   * Multi-service API routing configuration
   * Routes different API endpoints to their respective microservices
   */
  server: {
    port: 5173,
    host: true, // Allow external connections
    proxy: {
      // Authentication service - port 8000
      "/api/v1/auth": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/users": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/roles": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      
      // CRM service - port 8001
      "/api/v1/customers": {
        target: "http://localhost:8001",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/interactions": {
        target: "http://localhost:8001",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/feedback": {
        target: "http://localhost:8001",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/segments": {
        target: "http://localhost:8001",
        changeOrigin: true,
        secure: false,
      },
      
      // Booking service - port 8002
      "/api/v1/bookings": {
        target: "http://localhost:8002",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/reservations": {
        target: "http://localhost:8002",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/availability": {
        target: "http://localhost:8002",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/pricing": {
        target: "http://localhost:8002",
        changeOrigin: true,
        secure: false,
      },
      
      // Driver service - port 8003
      "/api/v1/drivers": {
        target: "http://localhost:8003",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/assignments": {
        target: "http://localhost:8003",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/incidents": {
        target: "http://localhost:8003",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/training": {
        target: "http://localhost:8003",
        changeOrigin: true,
        secure: false,
      },
      
      // Fleet service - port 8004
      "/api/v1/vehicles": {
        target: "http://localhost:8004",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/maintenance": {
        target: "http://localhost:8004",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/fleet": {
        target: "http://localhost:8004",
        changeOrigin: true,
        secure: false,
      },
      
      // Financial service - port 8005
      "/api/v1/invoices": {
        target: "http://localhost:8005",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/payments": {
        target: "http://localhost:8005",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/expenses": {
        target: "http://localhost:8005",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/analytics": {
        target: "http://localhost:8005",
        changeOrigin: true,
        secure: false,
      },
      
      // HR service - port 8006
      "/api/v1/employees": {
        target: "http://localhost:8006",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/schedules": {
        target: "http://localhost:8006",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/payroll": {
        target: "http://localhost:8006",
        changeOrigin: true,
        secure: false,
      },
      
      // Inventory service - port 8007
      "/api/v1/inventory": {
        target: "http://localhost:8007",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/parts": {
        target: "http://localhost:8007",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/suppliers": {
        target: "http://localhost:8007",
        changeOrigin: true,
        secure: false,
      },
      
      // Notification service - port 8008
      "/api/v1/notifications": {
        target: "http://localhost:8008",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/templates": {
        target: "http://localhost:8008",
        changeOrigin: true,
        secure: false,
      },
      
      // QA service - port 8009
      "/api/v1/quality": {
        target: "http://localhost:8009",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/audits": {
        target: "http://localhost:8009",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/reports": {
        target: "http://localhost:8009",
        changeOrigin: true,
        secure: false,
      },
      
      // Tour service - port 8010
      "/api/v1/tours": {
        target: "http://localhost:8010",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/packages": {
        target: "http://localhost:8010",
        changeOrigin: true,
        secure: false,
      },
      "/api/v1/guides": {
        target: "http://localhost:8010",
        changeOrigin: true,
        secure: false,
      },
      
      // Fallback for any other /api/v1 requests to auth service
      "/api/v1": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  optimizeDeps: { exclude: ["lucide-react"] },
});
