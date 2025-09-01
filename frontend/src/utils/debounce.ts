/**
 * Debounce utility for delaying function execution
 */

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

/**
 * Debounce hook for React components
 */
import { useCallback, useRef } from 'react';

export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): (...args: Parameters<T>) => void {
  const timeoutRef = useRef<NodeJS.Timeout>();

  return useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      timeoutRef.current = setTimeout(() => {
        callback(...args);
      }, delay);
    },
    [callback, delay]
  );
}

/**
 * Safe number conversion utilities
 */
export function safeNumber(value: string | number | null | undefined, defaultValue: number = 0): number {
  if (value === null || value === undefined || value === '') {
    return defaultValue;
  }
  
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return Number.isFinite(num) ? num : defaultValue;
}

export function isValidNumber(value: string | number | null | undefined): boolean {
  if (value === null || value === undefined || value === '') {
    return false;
  }
  
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return Number.isFinite(num) && num >= 0;
}

export function formatCurrencyInput(value: string): string {
  // Remove any non-numeric characters except decimal point
  const cleaned = value.replace(/[^\d.]/g, '');
  
  // Ensure only one decimal point
  const parts = cleaned.split('.');
  if (parts.length > 2) {
    return parts[0] + '.' + parts.slice(1).join('');
  }
  
  return cleaned;
}