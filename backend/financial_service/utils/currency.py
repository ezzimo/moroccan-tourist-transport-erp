"""
Currency conversion utilities
"""
from decimal import Decimal
from typing import Dict, Optional, List
import httpx
import redis
from datetime import datetime, timedelta
from config import settings


class CurrencyConverter:
    """Currency conversion service with caching"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.cache_ttl = 3600  # 1 hour cache
        self.base_currency = settings.default_currency
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """Get exchange rate between two currencies"""
        if from_currency == to_currency:
            return Decimal("1.0")
        
        # Check cache first
        cache_key = f"exchange_rate:{from_currency}:{to_currency}"
        cached_rate = self.redis.get(cache_key)
        
        if cached_rate:
            return Decimal(cached_rate)
        
        # Fetch from external API (mock implementation)
        rate = await self._fetch_exchange_rate(from_currency, to_currency)
        
        if rate:
            # Cache the rate
            self.redis.setex(cache_key, self.cache_ttl, str(rate))
        
        return rate
    
    async def convert_amount(
        self, 
        amount: Decimal, 
        from_currency: str, 
        to_currency: str
    ) -> Optional[Decimal]:
        """Convert amount from one currency to another"""
        rate = await self.get_exchange_rate(from_currency, to_currency)
        
        if rate is None:
            return None
        
        return amount * rate
    
    async def _fetch_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """Fetch exchange rate from external API (mock implementation)"""
        # Mock exchange rates for development
        # In production, integrate with a real currency API like:
        # - ExchangeRate-API
        # - Fixer.io
        # - CurrencyLayer
        
        mock_rates = {
            ("MAD", "EUR"): Decimal("0.094"),
            ("MAD", "USD"): Decimal("0.10"),
            ("EUR", "MAD"): Decimal("10.64"),
            ("EUR", "USD"): Decimal("1.06"),
            ("USD", "MAD"): Decimal("10.0"),
            ("USD", "EUR"): Decimal("0.94"),
        }
        
        rate = mock_rates.get((from_currency, to_currency))
        
        if rate:
            return rate
        
        # Try reverse rate
        reverse_rate = mock_rates.get((to_currency, from_currency))
        if reverse_rate:
            return Decimal("1.0") / reverse_rate
        
        return None
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        return settings.supported_currencies
    
    async def get_all_rates_to_base(self) -> Dict[str, Decimal]:
        """Get all exchange rates to base currency"""
        rates = {}
        
        for currency in settings.supported_currencies:
            if currency != self.base_currency:
                rate = await self.get_exchange_rate(currency, self.base_currency)
                if rate:
                    rates[currency] = rate
        
        return rates