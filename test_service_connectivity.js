#!/usr/bin/env node

/**
 * Test script to verify connectivity to all microservices
 * This helps diagnose if services are reachable and responding
 */

const http = require('http');

const services = [
  { name: 'Auth Service', port: 8000, path: '/api/v1/health' },
  { name: 'CRM Service', port: 8001, path: '/api/v1/health' },
  { name: 'Booking Service', port: 8002, path: '/api/v1/health' },
  { name: 'Driver Service', port: 8003, path: '/api/v1/health' },
  { name: 'Fleet Service', port: 8004, path: '/api/v1/health' },
  { name: 'Financial Service', port: 8005, path: '/api/v1/health' },
  { name: 'HR Service', port: 8006, path: '/api/v1/health' },
  { name: 'Inventory Service', port: 8007, path: '/api/v1/health' },
  { name: 'Notification Service', port: 8008, path: '/api/v1/health' },
  { name: 'QA Service', port: 8009, path: '/api/v1/health' },
  { name: 'Tour Service', port: 8010, path: '/api/v1/health' },
];

// Also test some actual endpoints
const endpoints = [
  { name: 'Auth Login', port: 8000, path: '/api/v1/auth/login', method: 'POST' },
  { name: 'CRM Customers', port: 8001, path: '/api/v1/customers/', method: 'GET' },
  { name: 'Booking List', port: 8002, path: '/api/v1/bookings/', method: 'GET' },
];

function testService(service) {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: service.port,
      path: service.path,
      method: service.method || 'GET',
      timeout: 5000,
    };

    const req = http.request(options, (res) => {
      resolve({
        ...service,
        status: res.statusCode,
        success: res.statusCode < 500,
        headers: res.headers,
      });
    });

    req.on('error', (err) => {
      resolve({
        ...service,
        status: 'ERROR',
        success: false,
        error: err.message,
      });
    });

    req.on('timeout', () => {
      resolve({
        ...service,
        status: 'TIMEOUT',
        success: false,
        error: 'Request timeout',
      });
    });

    req.end();
  });
}

async function runTests() {
  console.log('🔍 Testing Microservice Connectivity');
  console.log('=' * 50);

  console.log('\n📡 Health Check Tests:');
  for (const service of services) {
    const result = await testService(service);
    const status = result.success ? '✅' : '❌';
    const statusText = result.status === 'ERROR' ? result.error : result.status;
    console.log(`${status} ${service.name.padEnd(20)} → localhost:${service.port} (${statusText})`);
  }

  console.log('\n🎯 Endpoint Tests:');
  for (const endpoint of endpoints) {
    const result = await testService(endpoint);
    const status = result.success ? '✅' : '❌';
    const statusText = result.status === 'ERROR' ? result.error : result.status;
    console.log(`${status} ${endpoint.name.padEnd(20)} → localhost:${endpoint.port}${endpoint.path} (${statusText})`);
  }

  console.log('\n📊 Summary:');
  const allTests = [...services, ...endpoints];
  const successful = allTests.filter(async (test) => (await testService(test)).success).length;
  const total = allTests.length;
  console.log(`✅ Successful: ${successful}/${total}`);
  console.log(`❌ Failed: ${total - successful}/${total}`);
  
  if (successful < total) {
    console.log('\n💡 Troubleshooting Tips:');
    console.log('1. Ensure all microservices are running: docker compose ps');
    console.log('2. Check service logs: docker compose logs [service_name]');
    console.log('3. Verify port bindings: docker compose port [service_name] [port]');
    console.log('4. Test direct curl: curl http://localhost:8001/api/v1/health');
  }
}

runTests().catch(console.error);

