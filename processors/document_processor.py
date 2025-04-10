import os
import logging
from app import db
from models import Document, Page

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main document processor that delegates to specific processors based on file type"""
    
    def __init__(self, processors=None):
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
        try:
            file_extension = os.path.splitext(filename)[1].lower().strip('.')
            
            # Find appropriate processor
            processor = next(
                (p for p in self.processors if p.can_process(file_extension)), 
                None
            )
            
            if not processor:
                raise ValueError(f"No processor available for file type: {file_extension}")
            
            # Extract text from document
            pages_content = processor.extract_text(file_path)
            
            # Create document record
            document = Document(
                filename=filename,
                file_type=file_extension,
                page_count=len(pages_content)
            )
            db.session.add(document)
            db.session.flush()  # To get the document ID
            
            # Create page records
            for page_num, content in pages_content.items():
                page = Page(
                    document_id=document.id,
                    page_number=page_num,
                    content=content
                )
                db.session.add(page)
            
            db.session.commit()
            
            return document.id, document.page_count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing document: {str(e)}")
            raise
