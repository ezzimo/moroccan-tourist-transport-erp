import { test, expect } from '@playwright/test';

test.describe('Tour Operations Routes', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page and authenticate
    await page.goto('/login');
    
    // Fill login form with test credentials
    await page.fill('input[name="email"]', 'admin@example.com');
    await page.fill('input[name="password"]', 'ChangeMe!123');
    await page.click('button[type="submit"]');
    
    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard');
  });

  test('should navigate to tour templates page', async ({ page }) => {
    await page.goto('/tours/templates');
    
    await expect(page.locator('h1')).toContainText('Tour Templates');
    await expect(page.locator('text=Create and manage reusable tour templates')).toBeVisible();
  });

  test('should navigate to create tour template page', async ({ page }) => {
    await page.goto('/tours/templates/create');
    
    await expect(page.locator('h1')).toContainText('Create Tour Template');
    await expect(page.locator('text=Design a reusable tour template')).toBeVisible();
    
    // Check form elements are present
    await expect(page.locator('input[placeholder*="Imperial Cities"]')).toBeVisible();
    await expect(page.locator('select')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toContainText('Create Template');
  });

  test('should navigate to tour instances page', async ({ page }) => {
    await page.goto('/tours/instances');
    
    await expect(page.locator('h1')).toContainText('Tour Instances');
    await expect(page.locator('text=Track active, planned, and completed tours')).toBeVisible();
    
    // Check tabs are present
    await expect(page.locator('text=Active Tours')).toBeVisible();
    await expect(page.locator('text=Planned Tours')).toBeVisible();
    await expect(page.locator('text=Completed Tours')).toBeVisible();
  });

  test('should create a tour template', async ({ page }) => {
    await page.goto('/tours/templates/create');
    
    // Fill out the form
    await page.fill('input[placeholder*="Imperial Cities"]', 'Test Cultural Tour');
    await page.selectOption('select', 'Marrakech');
    await page.fill('input[type="number"][min="1"][max="30"]', '3');
    await page.fill('input[placeholder*="Brief description"]', 'A test cultural tour');
    
    // Select category (Cultural should be default)
    await page.click('button:has-text("Cultural")');
    
    // Set participants
    await page.fill('input[min="1"]:first', '2'); // min participants
    await page.fill('input[min="1"]:last', '12'); // max participants
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should redirect to templates list
    await page.waitForURL('/tours/templates');
    
    // Verify the new template appears (this might need adjustment based on actual API response)
    await expect(page.locator('text=Test Cultural Tour')).toBeVisible();
  });

  test('should switch between tour instance tabs', async ({ page }) => {
    await page.goto('/tours/instances');
    
    // Test tab switching
    await page.click('text=Planned Tours');
    await expect(page.locator('.border-orange-500')).toContainText('Planned Tours');
    
    await page.click('text=Completed Tours');
    await expect(page.locator('.border-orange-500')).toContainText('Completed Tours');
    
    await page.click('text=Active Tours');
    await expect(page.locator('.border-orange-500')).toContainText('Active Tours');
  });
});