import io
import logging
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Processor for PDF files"""
    
    def can_process(self, file_extension):
        """Check if this processor can handle the given file extension"""
        return file_extension.lower() == 'pdf'
    
    def extract_text(self, file_path):
        """
        Extract text from a PDF file, using OCR if needed
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            dict: A dictionary mapping page numbers to text content
        """
        try:
            pages_content = {}
            
            # Try extracting text directly first
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # If page has no text (might be an image-based PDF), use OCR
                    if not text or len(text.strip()) < 50:  # Arbitrary threshold to detect low text content
                        pages_content[page_num + 1] = self._extract_text_with_ocr(file_path, page_num)
                    else:
                        pages_content[page_num + 1] = text
            
            return pages_content
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    def _extract_text_with_ocr(self, pdf_path, page_num):
        """
        Extract text from a PDF page using OCR
        
        Args:
            pdf_path: Path to the PDF file
            page_num: Page number to process (0-based)
            
        Returns:
            str: Extracted text
        """
        try:
            # Convert PDF page to image
            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
            
            if not images:
                return ""
            
            # Use OCR to extract text from the image
            text = pytesseract.image_to_string(images[0])
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text with OCR: {str(e)}")
            return f"[OCR ERROR: {str(e)}]"
