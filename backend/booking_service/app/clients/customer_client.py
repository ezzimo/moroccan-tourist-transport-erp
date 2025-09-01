"""
Customer service client for validation
"""
import os
import logging
import httpx
from fastapi import HTTPException, status
from typing import Optional

logger = logging.getLogger(__name__)

CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://crm_service:8001")
DEV_BYPASS = os.getenv("ALLOW_DEV_CUSTOMER_BYPASS", "false").lower() == "true"


class CustomerClient:
    """Client for interacting with customer service"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or CUSTOMER_SERVICE_URL
        self.bypass_enabled = DEV_BYPASS
        
    async def verify_customer_exists(self, customer_id: str) -> bool:
        """Verify that a customer exists in the CRM service"""
        
        if self.bypass_enabled:
            logger.warning(f"DEV BYPASS: Skipping customer verification for {customer_id}")
            return True
        
        url = f"{self.base_url}/api/v1/customers/{customer_id}"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    logger.info(f"Customer {customer_id} verified successfully")
                    return True
                elif response.status_code == 404:
                    logger.warning(f"Customer {customer_id} not found")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Customer with ID {customer_id} does not exist. Please verify the customer ID."
                    )
                else:
                    logger.error(f"Customer service returned {response.status_code}: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Unable to verify customer information. Please try again later."
                    )
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout verifying customer {customer_id}")
            if self.bypass_enabled:
                logger.warning("DEV BYPASS: Allowing booking despite timeout")
                return True
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Customer verification service is temporarily unavailable. Please try again."
            )
        except httpx.RequestError as e:
            logger.error(f"Network error verifying customer {customer_id}: {e}")
            if self.bypass_enabled:
                logger.warning("DEV BYPASS: Allowing booking despite network error")
                return True
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to connect to customer verification service. Please try again."
            )
        except HTTPException:
            # Re-raise our own HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error verifying customer {customer_id}: {e}")
            if self.bypass_enabled:
                logger.warning("DEV BYPASS: Allowing booking despite unexpected error")
                return True
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during customer verification."
            )
    
    async def get_customer_info(self, customer_id: str) -> Optional[dict]:
        """Get customer information (optional, for enrichment)"""
        
        if self.bypass_enabled:
            return {
                "id": customer_id,
                "full_name": "Dev Bypass Customer",
                "email": "dev@example.com"
            }
        
        url = f"{self.base_url}/api/v1/customers/{customer_id}"
        
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Could not fetch customer info for {customer_id}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.warning(f"Failed to fetch customer info for {customer_id}: {e}")
            return None