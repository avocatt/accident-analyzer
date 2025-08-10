import base64
import os
from PIL import Image
import io
from typing import Dict, Any, Optional
import fitz  # PyMuPDF


class DocumentProcessor:
    """
    Processes documents and images for AI analysis
    """
    
    def __init__(self):
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        self.supported_doc_formats = ['.pdf'] + self.supported_image_formats
        
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document file (PDF or image) and prepare it for AI analysis
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self.process_pdf(file_path)
        elif file_ext in self.supported_image_formats:
            return self.process_image(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process PDF file - extract text and convert pages to images
        """
        result = {
            "type": "pdf",
            "text_content": "",
            "page_images": [],
            "page_count": 0
        }
        
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            result["page_count"] = len(doc)
            
            # Extract text from all pages
            text_content = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_content.append(page.get_text())
            result["text_content"] = "\n".join(text_content)
            
            # Convert each page to image for visual analysis
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Render page to image
                mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to base64
                base64_image = base64.b64encode(img_data).decode('utf-8')
                result["page_images"].append({
                    "page_number": page_num + 1,
                    "base64": base64_image,
                    "mime_type": "image/png"
                })
            
            doc.close()
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
        
        return result
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process image file - optimize and convert to base64
        """
        result = {
            "type": "image",
            "base64": "",
            "mime_type": "",
            "dimensions": None
        }
        
        try:
            # Open and process image
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                
                # Store dimensions
                result["dimensions"] = {"width": img.width, "height": img.height}
                
                # Resize if image is too large (max 2000px on longest side)
                max_size = 2000
                if max(img.width, img.height) > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffered = io.BytesIO()
                img.save(buffered, format='JPEG', quality=85, optimize=True)
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                result["base64"] = img_str
                result["mime_type"] = "image/jpeg"
                
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
        
        return result
    
    def validate_file_size(self, file_path: str, max_size_mb: int = 10) -> bool:
        """
        Validate that file size is within acceptable limits
        """
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
        return file_size <= max_size_mb
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic information about a file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_stats = os.stat(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        return {
            "filename": os.path.basename(file_path),
            "extension": file_ext,
            "size_bytes": file_stats.st_size,
            "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
            "is_supported": file_ext in self.supported_doc_formats
        }