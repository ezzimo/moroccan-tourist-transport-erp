#!/usr/bin/env node
/**
 * Check tour-related routes and configurations
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Tour Routes Configuration Check');
console.log('=' * 50);

// Check Vite proxy configuration
const viteConfigPath = path.join('frontend', 'vite.config.ts');
if (fs.existsSync(viteConfigPath)) {
    const viteConfig = fs.readFileSync(viteConfigPath, 'utf8');
    
    console.log('\n📋 Vite Proxy Configuration:');
    
    // Look for tour-related proxy rules
    const tourProxyRules = [
        '/api/v1/tours',
        '/api/v1/tour-templates',
        '/api/v1/tour-instances',
        '/api/v1/itinerary',
        '/api/v1/incidents'
    ];
    
    tourProxyRules.forEach(rule => {
        if (viteConfig.includes(rule)) {
            console.log(`✅ Found proxy rule: ${rule}`);
            
            // Extract target
            const ruleRegex = new RegExp(`"${rule.replace(/\//g, '\\/')}"[^}]*target:[^"]*"([^"]*)"`, 'g');
            const match = ruleRegex.exec(viteConfig);
            if (match) {
                console.log(`   → Target: ${match[1]}`);
            }
        } else {
            console.log(`❌ Missing proxy rule: ${rule}`);
        }
    });
} else {
    console.log('❌ Vite config not found');
}

// Check tour service configuration
const tourConfigPath = path.join('backend', 'tour_service', 'config.py');
if (fs.existsSync(tourConfigPath)) {
    console.log('\n🎯 Tour Service Configuration:');
    const tourConfig = fs.readFileSync(tourConfigPath, 'utf8');
    
    // Check for key configuration items
    const configChecks = [
        'auth_service_url',
        'secret_key',
        'allowed_origins',
        'database_url'
    ];
    
    configChecks.forEach(check => {
        if (tourConfig.includes(check)) {
            console.log(`✅ Found config: ${check}`);
        } else {
            console.log(`❌ Missing config: ${check}`);
        }
    });
} else {
    console.log('❌ Tour service config not found');
}

// Check frontend tour components
const tourPagesPath = path.join('frontend', 'src', 'tour', 'pages');
if (fs.existsSync(tourPagesPath)) {
    console.log('\n📱 Frontend Tour Pages:');
    const tourPages = fs.readdirSync(tourPagesPath);
    tourPages.forEach(page => {
        console.log(`✅ Found page: ${page}`);
    });
} else {
    console.log('❌ Tour pages directory not found');
}

// Check App.tsx routing
const appPath = path.join('frontend', 'src', 'App.tsx');
if (fs.existsSync(appPath)) {
    console.log('\n🛣️  App.tsx Route Configuration:');
    const appContent = fs.readFileSync(appPath, 'utf8');
    
    const tourRoutes = [
        'path="tours"',
        'path="tours/templates"',
        'ToursPage',
        'TourTemplatesPage'
    ];
    
    tourRoutes.forEach(route => {
        if (appContent.includes(route)) {
            console.log(`✅ Found route: ${route}`);
        } else {
            console.log(`❌ Missing route: ${route}`);
        }
    });
} else {
    console.log('❌ App.tsx not found');
}

console.log('\n📊 Check Complete');
console.log('Run this script to identify configuration issues before testing');