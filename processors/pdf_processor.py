import os
import io
import PyPDF2
import pdf2image
import pytesseract
from PIL import Image


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
        # Open the PDF file
        pages = {}
        
        try:
            with open(file_path, 'rb') as file:
                # Create a PDF reader object
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Process each page
                for page_num in range(len(pdf_reader.pages)):
                    # Try to extract text directly first
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # If no text is extracted, try OCR
                    if not text or len(text.strip()) < 50:  # Arbitrary threshold
                        text = self._extract_text_with_ocr(file_path, page_num)
                    
                    # Store the extracted text
                    pages[page_num + 1] = text  # 1-based page numbering
        
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")
        
        return pages
    
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
            images = pdf2image.convert_from_path(
                pdf_path, 
                first_page=page_num+1, 
                last_page=page_num+1,
                dpi=300
            )
            
            if not images:
                return ""
            
            # Apply OCR to the image
            image = images[0]
            text = pytesseract.image_to_string(image)
            
            return text
        
        except Exception as e:
            print(f"OCR failed on page {page_num+1}: {str(e)}")
            return ""