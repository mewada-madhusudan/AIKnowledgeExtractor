import docx


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
            # Open the DOCX file
            doc = docx.Document(file_path)
            
            # Extract all paragraphs
            paragraphs = [p.text for p in doc.paragraphs]
            
            # Combine all paragraphs
            text = '\n'.join(paragraphs)
            
            # DOCX doesn't really have pages, so we'll treat the whole document as one page
            return {1: text}
            
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")