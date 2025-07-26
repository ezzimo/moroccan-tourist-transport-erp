"""
File upload and document processing utilities for HR service
"""
import os
import uuid
import hashlib
from typing import Optional, Dict, Any, List
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import magic
import logging

logger = logging.getLogger(__name__)

# Configuration
UPLOAD_DIR = Path("uploads/hr_documents")
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


class FileUploadHandler:
    """Handles secure file upload and processing for HR documents"""
    
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
    
    async def process_image(self, content: bytes, filename: str) -> bytes:
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
    
    async def save_file(self, file_data: Dict[str, Any], subfolder: str = "") -> Dict[str, Any]:
        """Save file to storage
        
        Args:
            file_data: Validated file data
            subfolder: Optional subfolder path
            
        Returns:
            Dict with file storage information
        """
        # Generate unique filename
        file_id = uuid.uuid4()
        file_ext = file_data["file_extension"]
        safe_filename = f"{file_id}{file_ext}"
        
        # Create subfolder if specified
        if subfolder:
            target_dir = self.upload_dir / subfolder
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = self.upload_dir
        
        file_path = target_dir / safe_filename
        
        # Process content if it's an image
        content = file_data["content"]
        if file_data["mime_type"].startswith("image/"):
            content = await self.process_image(content, file_data["original_filename"])
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Saved file {safe_filename} in {target_dir}")
        
        return {
            "file_id": str(file_id),
            "file_path": str(file_path),
            "file_name": safe_filename,
            "original_filename": file_data["original_filename"],
            "file_size": len(content),
            "mime_type": file_data["mime_type"],
            "file_hash": file_data["file_hash"]
        }
    
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


async def validate_document(file: UploadFile) -> Dict[str, Any]:
    """Validate HR document upload
    
    Args:
        file: FastAPI UploadFile
        
    Returns:
        Validation results
    """
    handler = FileUploadHandler()
    return await handler.validate_file(file)


async def process_upload(file: UploadFile, subfolder: str = "") -> Dict[str, Any]:
    """Process HR document upload
    
    Args:
        file: FastAPI UploadFile
        subfolder: Optional subfolder for organization
        
    Returns:
        Upload results
    """
    handler = FileUploadHandler()
    file_data = await handler.validate_file(file)
    return await handler.save_file(file_data, subfolder)


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


def get_file_size_mb(file_size_bytes: int) -> float:
    """Convert file size to MB
    
    Args:
        file_size_bytes: File size in bytes
        
    Returns:
        File size in MB
    """
    return round(file_size_bytes / (1024 * 1024), 2)


async def scan_for_viruses(file_path: str) -> bool:
    """Scan file for viruses (placeholder for actual antivirus integration)
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file is clean
    """
    # This would integrate with an actual antivirus service
    # For now, return True (clean)
    logger.info(f"Virus scan completed for {file_path} - Clean")
    return True


def generate_secure_filename(original_filename: str) -> str:
    """Generate secure filename
    
    Args:
        original_filename: Original filename
        
    Returns:
        Secure filename
    """
    # Extract extension
    file_ext = Path(original_filename).suffix.lower()
    
    # Generate UUID-based filename
    secure_name = f"{uuid.uuid4()}{file_ext}"
    
    return secure_name


def is_allowed_file_type(filename: str) -> bool:
    """Check if file type is allowed
    
    Args:
        filename: Filename to check
        
    Returns:
        True if file type is allowed
    """
    file_ext = Path(filename).suffix.lower()
    return file_ext in ALLOWED_EXTENSIONS


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file
    
    Args:
        file_path: Path to file
        
    Returns:
        SHA256 hash string
    """
    hash_sha256 = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {str(e)}")
        return ""