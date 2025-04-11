import pytesseract
from PIL import Image


class ImageProcessor:
    """Processor for image files (JPG, PNG, etc.)"""
    
    def can_process(self, file_extension):
        """Check if this processor can handle the given file extension"""
        return file_extension.lower() in ['jpg', 'jpeg', 'png']
    
    def extract_text(self, file_path):
        """
        Extract text from an image file using OCR
        
        Args:
            file_path: Path to the image file
            
        Returns:
            dict: A dictionary mapping page numbers to text content
        """
        try:
            # Open the image
            image = Image.open(file_path)
            
            # Use OCR to extract text
            text = pytesseract.image_to_string(image)
            
            # Return as a single page
            return {1: text}
            
        except Exception as e:
            raise Exception(f"Failed to extract text from image: {str(e)}")