#!/usr/bin/env node

/**
 * Test script to validate frontend API routing configuration
 * This script checks if the Vite proxy configuration correctly routes
 * different API endpoints to their respective microservices.
 */

const fs = require('fs');
const path = require('path');

// Read the Vite configuration
const viteConfigPath = path.join(__dirname, 'frontend', 'vite.config.ts');
const viteConfig = fs.readFileSync(viteConfigPath, 'utf8');

// Expected service mappings
const expectedMappings = {
  '/api/v1/auth': 'localhost:8000',
  '/api/v1/users': 'localhost:8000',
  '/api/v1/roles': 'localhost:8000',
  '/api/v1/customers': 'localhost:8001',
  '/api/v1/interactions': 'localhost:8001',
  '/api/v1/feedback': 'localhost:8001',
  '/api/v1/segments': 'localhost:8001',
  '/api/v1/bookings': 'localhost:8002',
  '/api/v1/reservations': 'localhost:8002',
  '/api/v1/availability': 'localhost:8002',
  '/api/v1/pricing': 'localhost:8002',
  '/api/v1/drivers': 'localhost:8003',
  '/api/v1/assignments': 'localhost:8003',
  '/api/v1/incidents': 'localhost:8003',
  '/api/v1/training': 'localhost:8003',
  '/api/v1/vehicles': 'localhost:8004',
  '/api/v1/maintenance': 'localhost:8004',
  '/api/v1/fleet': 'localhost:8004',
  '/api/v1/invoices': 'localhost:8005',
  '/api/v1/payments': 'localhost:8005',
  '/api/v1/expenses': 'localhost:8005',
  '/api/v1/analytics': 'localhost:8005',
  '/api/v1/employees': 'localhost:8006',
  '/api/v1/schedules': 'localhost:8006',
  '/api/v1/payroll': 'localhost:8006',
  '/api/v1/inventory': 'localhost:8007',
  '/api/v1/parts': 'localhost:8007',
  '/api/v1/suppliers': 'localhost:8007',
  '/api/v1/notifications': 'localhost:8008',
  '/api/v1/templates': 'localhost:8008',
  '/api/v1/quality': 'localhost:8009',
  '/api/v1/audits': 'localhost:8009',
  '/api/v1/reports': 'localhost:8009',
  '/api/v1/tours': 'localhost:8010',
  '/api/v1/packages': 'localhost:8010',
  '/api/v1/guides': 'localhost:8010',
};

console.log('🔍 Testing Frontend API Routing Configuration');
console.log('=' * 50);

let passed = 0;
let failed = 0;

// Test each expected mapping
for (const [endpoint, expectedTarget] of Object.entries(expectedMappings)) {
  const regex = new RegExp(`"${endpoint.replace(/\//g, '\\/')}": {[^}]*target: "http://${expectedTarget.replace(/\./g, '\\.')}"`, 'g');
  
  if (regex.test(viteConfig)) {
    console.log(`✅ ${endpoint} → ${expectedTarget}`);
    passed++;
  } else {
    console.log(`❌ ${endpoint} → ${expectedTarget} (NOT FOUND)`);
    failed++;
  }
}

// Check for fallback configuration
const fallbackRegex = /"\/api\/v1": {[^}]*target: "http:\/\/localhost:8000"/g;
if (fallbackRegex.test(viteConfig)) {
  console.log(`✅ Fallback /api/v1 → localhost:8000`);
  passed++;
} else {
  console.log(`❌ Fallback /api/v1 → localhost:8000 (NOT FOUND)`);
  failed++;
}

console.log('\n📊 Test Results:');
console.log(`✅ Passed: ${passed}`);
console.log(`❌ Failed: ${failed}`);
console.log(`📈 Success Rate: ${Math.round((passed / (passed + failed)) * 100)}%`);

if (failed === 0) {
  console.log('\n🎉 All routing configurations are correct!');
  process.exit(0);
} else {
  console.log('\n⚠️  Some routing configurations need attention.');
  process.exit(1);
}

