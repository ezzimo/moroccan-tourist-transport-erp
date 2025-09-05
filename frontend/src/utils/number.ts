/**
 * Safe number utilities for handling monetary values and formatting
 */

export const isFiniteNumber = (v: unknown): v is number =>
  typeof v === "number" && Number.isFinite(v);

export const toNumber = (v: unknown, fallback = 0): number => {
  if (isFiniteNumber(v)) return v;
  if (typeof v === "string" && v.trim() !== "" && !Number.isNaN(Number(v))) {
    return Number(v);
  }
  return fallback;
};

export const formatMoney = (v: unknown, digits = 2, currency = 'MAD'): string => {
  const n = toNumber(v, 0);
  // toFixed is only called on a guaranteed number
  return `${n.toFixed(digits)} ${currency}`;
};

export const formatMoneyValue = (v: unknown, digits = 2): string => {
  const n = toNumber(v, 0);
  return n.toFixed(digits);
};

export const isValidNumber = (value: string | number | null | undefined): boolean => {
  if (value === null || value === undefined || value === '') {
    return false;
  }
  
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return Number.isFinite(num) && num >= 0;
};

export const formatCurrencyInput = (value: string): string => {
  // Remove any non-numeric characters except decimal point
  const cleaned = value.replace(/[^\d.]/g, '');
  
  // Ensure only one decimal point
  const parts = cleaned.split('.');
  if (parts.length > 2) {
    return parts[0] + '.' + parts.slice(1).join('');
  }
  
  return cleaned;
};

export const safeNumber = (value: string | number | null | undefined, defaultValue: number = 0): number => {
  if (value === null || value === undefined || value === '') {
    return defaultValue;
  }
  
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return Number.isFinite(num) ? num : defaultValue;
};