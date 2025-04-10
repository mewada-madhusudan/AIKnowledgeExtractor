import logging
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

class DocxProcessor:
    """Processor for DOCX files"""
    
    def can_process(self, file_extension):
        """Check if this processor can handle the given file extension"""
        return file_extension.lower() == 'docx'
    
    def extract_text(self, file_path):
        """
        Extract text from a DOCX file
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            dict: A dictionary mapping page numbers to text content
        """
        try:
            # Note: DOCX doesn't have explicit page breaks in its structure
            # We'll simply treat the whole document as one page initially
            # A more advanced implementation could try to estimate page breaks
            
            doc = DocxDocument(file_path)
            
            # Extract text from paragraphs
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        row_text.append(cell.text)
                    full_text.append(" | ".join(row_text))
            
            # Since DOCX doesn't have explicit pages, we'll create a single page
            # A more advanced implementation could split by estimated page breaks
            return {1: "\n".join(full_text)}
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise
