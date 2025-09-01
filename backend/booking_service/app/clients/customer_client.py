"""
Customer service client for verification
"""
import logging
import httpx
from fastapi import HTTPException, status
from config import settings

logger = logging.getLogger(__name__)


class CustomerClient:
    """Client for communicating with the customer service"""
    
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.CUSTOMER_SERVICE_URL
        self._timeout = 10

    async def verify_customer(self, customer_id: str, access_token: str | None = None) -> dict:
        """
        Verify customer exists and return customer data
        
        Args:
            customer_id: UUID of the customer to verify
            access_token: JWT token to forward for authentication
            
        Returns:
            Customer data dictionary
            
        Raises:
            HTTPException: If customer not found or service unavailable
        """
        url = f"{self.base_url}/customers/{customer_id}"
        headers = {}
        
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                logger.debug("Verifying customer %s at %s", customer_id, url)
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    customer_data = response.json()
                    logger.info("Customer %s verified successfully", customer_id)
                    return customer_data
                    
                elif response.status_code == 404:
                    logger.warning("Customer %s not found", customer_id)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Customer {customer_id} not found"
                    )
                    
                elif response.status_code == 401:
                    logger.warning("Unauthorized access to customer service")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Unauthorized access to customer information"
                    )
                    
                else:
                    logger.error("Customer service returned %s: %s", response.status_code, response.text)
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Unable to verify customer information"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Timeout verifying customer %s", customer_id)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Customer service timeout"
            )
        except httpx.RequestError as e:
            logger.error("Network error verifying customer %s: %s", customer_id, e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to connect to customer service"
            )