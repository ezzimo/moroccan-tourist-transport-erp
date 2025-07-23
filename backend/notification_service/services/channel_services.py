"""
Channel-specific services for sending notifications
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
import httpx
import json
from config import settings


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.from_email = settings.default_from_email
        self.from_name = settings.default_from_name
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        recipient_name: Optional[str] = None,
        is_html: bool = False
    ) -> bool:
        """Send email notification"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Create the HTML/text part
            if is_html:
                part = MIMEText(body, "html")
            else:
                part = MIMEText(body, "plain")
            
            message.attach(part)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls(context=context)
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.sendmail(self.from_email, to_email, message.as_string())
            
            return True
            
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False


class SMSService:
    """Service for sending SMS notifications via Twilio"""
    
    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.from_phone = settings.twilio_phone_number
    
    async def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS notification"""
        if not self.account_sid or not self.auth_token:
            print("SMS service not configured - using mock")
            return await self._mock_send_sms(to_phone, message)
        
        try:
            # Use Twilio API
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            
            data = {
                "From": self.from_phone,
                "To": to_phone,
                "Body": message
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=(self.account_sid, self.auth_token),
                    timeout=settings.notification_timeout_seconds
                )
                
                return response.status_code == 201
                
        except Exception as e:
            print(f"SMS sending failed: {str(e)}")
            return False
    
    async def _mock_send_sms(self, to_phone: str, message: str) -> bool:
        """Mock SMS sending for development"""
        print(f"[MOCK SMS] To: {to_phone}")
        print(f"[MOCK SMS] Message: {message}")
        return True


class PushService:
    """Service for sending push notifications via Firebase"""
    
    def __init__(self):
        self.server_key = settings.firebase_server_key
        self.project_id = settings.firebase_project_id
    
    async def send_push(
        self, 
        token: str, 
        title: str, 
        body: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send push notification"""
        if not self.server_key:
            print("Push service not configured - using mock")
            return await self._mock_send_push(token, title, body, data)
        
        try:
            url = "https://fcm.googleapis.com/fcm/send"
            
            headers = {
                "Authorization": f"key={self.server_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "to": token,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
            
            if data:
                payload["data"] = data
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=settings.notification_timeout_seconds
                )
                
                return response.status_code == 200
                
        except Exception as e:
            print(f"Push notification failed: {str(e)}")
            return False
    
    async def _mock_send_push(
        self, 
        token: str, 
        title: str, 
        body: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mock push notification for development"""
        print(f"[MOCK PUSH] Token: {token[:20]}...")
        print(f"[MOCK PUSH] Title: {title}")
        print(f"[MOCK PUSH] Body: {body}")
        if data:
            print(f"[MOCK PUSH] Data: {data}")
        return True


class WhatsAppService:
    """Service for sending WhatsApp messages"""
    
    def __init__(self):
        self.api_url = settings.whatsapp_api_url
        self.api_token = settings.whatsapp_api_token
    
    async def send_message(self, to_phone: str, message: str) -> bool:
        """Send WhatsApp message"""
        if not self.api_url or not self.api_token:
            print("WhatsApp service not configured - using mock")
            return await self._mock_send_whatsapp(to_phone, message)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "to": to_phone,
                "message": message
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=settings.notification_timeout_seconds
                )
                
                return response.status_code == 200
                
        except Exception as e:
            print(f"WhatsApp sending failed: {str(e)}")
            return False
    
    async def _mock_send_whatsapp(self, to_phone: str, message: str) -> bool:
        """Mock WhatsApp sending for development"""
        print(f"[MOCK WHATSAPP] To: {to_phone}")
        print(f"[MOCK WHATSAPP] Message: {message}")
        return True


class WebhookService:
    """Service for sending webhook notifications"""
    
    async def send_webhook(
        self, 
        url: str, 
        payload: Dict[str, Any], 
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """Send webhook notification"""
        try:
            webhook_headers = {"Content-Type": "application/json"}
            if headers:
                webhook_headers.update(headers)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=webhook_headers,
                    json=payload,
                    timeout=settings.webhook_timeout_seconds
                )
                
                return 200 <= response.status_code < 300
                
        except Exception as e:
            print(f"Webhook sending failed: {str(e)}")
            return False