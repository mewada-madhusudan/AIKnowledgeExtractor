import os
from models import Document, Page
from database import db


class DocumentProcessor:
    """Main document processor that delegates to specific processors based on file type"""
    
    def __init__(self, processors=None):
        """Initialize with a list of document processors"""
        self.processors = processors or []
    
    def process(self, file_path, filename):
        """
        Process a document file, extract text and store in the database
        
        Args:
            file_path: Path to the document file
            filename: Original filename
            
        Returns:
            tuple: (document_id, page_count)
        """
        # Get file extension
        _, file_extension = os.path.splitext(filename)
        file_extension = file_extension[1:].lower()  # Remove the dot and convert to lowercase
        
        # Find appropriate processor
        processor = None
        for p in self.processors:
            if p.can_process(file_extension):
                processor = p
                break
        
        if not processor:
            raise ValueError(f"No processor available for file type: {file_extension}")
        
        # Extract text from document
        pages = processor.extract_text(file_path)
        
        if not pages:
            raise ValueError("No text could be extracted from the document")
        
        # Create document record
        document = Document(
            filename=filename,
            file_type=file_extension,
            page_count=len(pages)
        )
        db.session.add(document)
        db.session.flush()  # Get the document ID
        
        # Create page records
        for page_num, content in pages.items():
            page = Page(
                document_id=document.id,
                page_number=page_num,
                content=content
            )
            db.session.add(page)
        
        # Commit to database
        db.session.commit()
        
        # Clean up the temporary file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore errors in cleanup
        
        return document.id, len(pages)