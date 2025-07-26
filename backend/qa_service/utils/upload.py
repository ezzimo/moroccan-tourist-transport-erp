"""
File upload utilities for QA service
"""
import os
import uuid
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import magic
import logging

logger = logging.getLogger(__name__)

# Configuration
UPLOAD_DIR = Path("uploads/qa_documents")
CERTIFICATE_DIR = Path("uploads/certificates")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg", 
    "image/png",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

# Image processing settings
MAX_IMAGE_WIDTH = 2048
MAX_IMAGE_HEIGHT = 2048
IMAGE_QUALITY = 85


class QAFileUploadHandler:
    """Handles secure file upload for QA documents"""
    
    def __init__(self, upload_dir: Optional[Path] = None):
        self.upload_dir = upload_dir or UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded file
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            Dict with validation results
            
        Raises:
            HTTPException: If file validation fails
        """
        # Check file size
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension {file_ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content for MIME type validation
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Validate MIME type using python-magic
        mime_type = magic.from_buffer(content, mime=True)
        if mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {mime_type} not allowed"
            )
        
        # Calculate file hash for deduplication
        file_hash = hashlib.sha256(content).hexdigest()
        
        return {
            "original_filename": file.filename,
            "file_extension": file_ext,
            "mime_type": mime_type,
            "file_size": len(content),
            "file_hash": file_hash,
            "content": content
        }
    
    async def save_file(self, file_data: Dict[str, Any], entity_id: uuid.UUID, file_type: str = "document") -> Dict[str, Any]:
        """Save file to storage
        
        Args:
            file_data: Validated file data
            entity_id: Entity UUID (audit, certification, etc.)
            file_type: Type of file (document, certificate, etc.)
            
        Returns:
            Dict with file storage information
        """
        # Generate unique filename
        file_id = uuid.uuid4()
        file_ext = file_data["file_extension"]
        safe_filename = f"{entity_id}_{file_type}_{file_id}{file_ext}"
        
        # Create entity-specific directory
        entity_dir = self.upload_dir / str(entity_id)
        entity_dir.mkdir(exist_ok=True)
        
        file_path = entity_dir / safe_filename
        
        # Process content if it's an image
        content = file_data["content"]
        if file_data["mime_type"].startswith("image/"):
            content = await self._process_image(content, file_data["original_filename"])
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Saved {file_type} file {safe_filename} for entity {entity_id}")
        
        return {
            "file_id": str(file_id),
            "file_path": str(file_path),
            "file_name": safe_filename,
            "original_filename": file_data["original_filename"],
            "file_size": len(content),
            "mime_type": file_data["mime_type"],
            "file_hash": file_data["file_hash"]
        }
    
    async def _process_image(self, content: bytes, filename: str) -> bytes:
        """Process and optimize image files
        
        Args:
            content: Image file content
            filename: Original filename
            
        Returns:
            Processed image content
        """
        try:
            import io
            # Open image with PIL
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large
            if image.width > MAX_IMAGE_WIDTH or image.height > MAX_IMAGE_HEIGHT:
                image.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)
                logger.info(f"Resized image {filename} to {image.width}x{image.height}")
            
            # Save optimized image
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error processing image {filename}: {str(e)}")
            return content  # Return original if processing fails
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage
        
        Args:
            file_path: Path to file
            
        Returns:
            True if deleted successfully
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False


# Convenience functions for specific QA file types

async def process_audit_document_upload(file: UploadFile, audit_id: uuid.UUID) -> Dict[str, Any]:
    """Process audit document upload
    
    Args:
        file: FastAPI UploadFile
        audit_id: Audit UUID
        
    Returns:
        Upload results
    """
    handler = QAFileUploadHandler()
    file_data = await handler.validate_file(file)
    return await handler.save_file(file_data, audit_id, "audit_document")


async def process_certificate_upload(file: UploadFile, certification_id: uuid.UUID) -> Dict[str, Any]:
    """Process certificate upload
    
    Args:
        file: FastAPI UploadFile
        certification_id: Certification UUID
        
    Returns:
        Upload results
    """
    handler = QAFileUploadHandler(CERTIFICATE_DIR)
    file_data = await handler.validate_file(file)
    return await handler.save_file(file_data, certification_id, "certificate")


async def process_compliance_evidence_upload(file: UploadFile, requirement_id: uuid.UUID) -> Dict[str, Any]:
    """Process compliance evidence upload
    
    Args:
        file: FastAPI UploadFile
        requirement_id: Requirement UUID
        
    Returns:
        Upload results
    """
    handler = QAFileUploadHandler()
    file_data = await handler.validate_file(file)
    return await handler.save_file(file_data, requirement_id, "compliance_evidence")


def delete_audit_document(file_path: str) -> bool:
    """Delete audit document file
    
    Args:
        file_path: Path to file
        
    Returns:
        True if deleted successfully
    """
    handler = QAFileUploadHandler()
    return handler.delete_file(file_path)


def delete_certificate_file(file_path: str) -> bool:
    """Delete certificate file
    
    Args:
        file_path: Path to file
        
    Returns:
        True if deleted successfully
    """
    handler = QAFileUploadHandler(CERTIFICATE_DIR)
    return handler.delete_file(file_path)


def get_file_info(file_path: str) -> Optional[Dict[str, Any]]:
    """Get file information
    
    Args:
        file_path: Path to file
        
    Returns:
        File information or None if not found
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        
        stat = path.stat()
        return {
            "file_path": str(path),
            "file_name": path.name,
            "file_size": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime
        }
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {str(e)}")
        return None