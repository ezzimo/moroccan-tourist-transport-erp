"""
Customer service client with explicit error handling
"""
import os
import httpx
import logging
from fastapi import HTTPException, status
from typing import Optional

logger = logging.getLogger(__name__)

CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://crm_service:8001")


class CustomerClient:
    """Client for interacting with the CRM/Customer service"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or CUSTOMER_SERVICE_URL
        self._bypass = os.getenv("ALLOW_DEV_CUSTOMER_BYPASS", "false").lower() == "true"
        
    async def verify_customer_exists(self, customer_id: str) -> bool:
        """
        Verify that a customer exists in the CRM service
        
        Args:
            customer_id: UUID string of the customer
            
        Returns:
            bool: True if customer exists
            
        Raises:
            HTTPException: 400 if customer not found, 502 if service unavailable
        """
        if self._bypass:
            logger.warning("Customer verification bypassed for development (customer_id=%s)", customer_id)
            return True
            
        url = f"{self.base_url}/api/v1/customers/{customer_id}"
        
        try:
            logger.debug("Verifying customer exists: %s", url)
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                
            if response.status_code == 200:
                logger.debug("Customer %s verified successfully", customer_id)
                return True
            elif response.status_code == 404:
                logger.warning("Customer %s not found in CRM service", customer_id)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Customer with ID {customer_id} not found"
                )
            elif response.status_code >= 500:
                logger.error("CRM service error (status=%d) when verifying customer %s", 
                           response.status_code, customer_id)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Unable to verify customer information - CRM service unavailable"
                )
            else:
                logger.error("Unexpected response (status=%d) when verifying customer %s", 
                           response.status_code, customer_id)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Unable to verify customer information"
                )
                
        except httpx.TimeoutException:
            logger.error("Timeout when verifying customer %s", customer_id)
            if self._bypass:
                logger.warning("Customer verification timeout bypassed for development")
                return True
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Customer verification timeout - please try again"
            )
        except httpx.RequestError as e:
            logger.error("Network error when verifying customer %s: %s", customer_id, e)
            if self._bypass:
                logger.warning("Customer verification network error bypassed for development")
                return True
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to connect to customer service"
            )
        except HTTPException:
            # Re-raise our own HTTP exceptions
            raise
        except Exception as e:
            logger.exception("Unexpected error verifying customer %s: %s", customer_id, e)
            if self._bypass:
                logger.warning("Customer verification error bypassed for development")
                return True
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Customer verification failed"
            )

    async def get_customer_info(self, customer_id: str) -> Optional[dict]:
        """
        Get customer information from CRM service
        
        Args:
            customer_id: UUID string of the customer
            
        Returns:
            dict: Customer information or None if not available
        """
        if self._bypass:
            return {"id": customer_id, "name": "Dev Customer", "email": "dev@example.com"}
            
        url = f"{self.base_url}/api/v1/customers/{customer_id}"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning("Could not fetch customer info for %s (status=%d)", 
                             customer_id, response.status_code)
                return None
                
        except Exception as e:
            logger.warning("Error fetching customer info for %s: %s", customer_id, e)
            return None