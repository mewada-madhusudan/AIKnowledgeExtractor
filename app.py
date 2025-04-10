import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import tempfile

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///docprocessor.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure upload folder
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'png', 'jpg', 'jpeg'}

# Initialize the database
db.init_app(app)

# Import models and create tables
with app.app_context():
    # Import models here
    from models import Document, Page, ExtractionRule, ExtractionResult
    db.create_all()

# Import processors
from processors.document_processor import DocumentProcessor
from processors.pdf_processor import PDFProcessor
from processors.docx_processor import DocxProcessor
from processors.image_processor import ImageProcessor

# Import extractors
from extractors.pattern_extractor import PatternExtractor

# Initialize the document processor with specific processors
document_processor = DocumentProcessor([
    PDFProcessor(),
    DocxProcessor(),
    ImageProcessor()
])

# Initialize the pattern extractor
pattern_extractor = PatternExtractor()


def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/documents', methods=['GET'])
def list_documents():
    """List all processed documents"""
    documents = Document.query.all()
    return render_template('documents.html', documents=documents)


@app.route('/upload', methods=['POST'])
def upload_document():
    """Handle document upload and processing"""
    if 'document' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['document']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the document
            doc_id, page_count = document_processor.process(filepath, filename)
            
            flash(f'Document "{filename}" processed successfully with {page_count} pages', 'success')
            return redirect(url_for('list_documents'))
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            flash(f'Error processing document: {str(e)}', 'error')
            return redirect(request.url)
    else:
        flash(f'File type not allowed. Allowed types: {", ".join(app.config["ALLOWED_EXTENSIONS"])}', 'error')
        return redirect(request.url)


@app.route('/extract', methods=['GET', 'POST'])
def extract_data():
    """Handle extraction request"""
    documents = Document.query.all()
    
    if request.method == 'POST':
        # Get form data
        doc_ids = request.form.getlist('document_ids')
        excel_file = request.files.get('excel_file')
        
        if not doc_ids:
            flash('Please select at least one document', 'error')
            return redirect(request.url)
        
        if not excel_file:
            flash('Please upload an Excel file with extraction rules', 'error')
            return redirect(request.url)
        
        try:
            # Save Excel file
            excel_filename = secure_filename(excel_file.filename)
            excel_filepath = os.path.join(app.config['UPLOAD_FOLDER'], excel_filename)
            excel_file.save(excel_filepath)
            
            # Load rules from Excel
            rules = pattern_extractor.load_rules_from_excel(excel_filepath)
            
            # Store rules in session for later use
            session['extraction_rules'] = rules
            session['document_ids'] = doc_ids
            
            # Redirect to results
            return redirect(url_for('show_results'))
        except Exception as e:
            logger.error(f"Error setting up extraction: {str(e)}")
            flash(f'Error setting up extraction: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('extract.html', documents=documents)


@app.route('/results')
def show_results():
    """Show extraction results"""
    # Get data from session
    rules = session.get('extraction_rules')
    doc_ids = session.get('document_ids')
    
    if not rules or not doc_ids:
        flash('No extraction setup found', 'error')
        return redirect(url_for('extract_data'))
    
    try:
        # Get documents
        documents = Document.query.filter(Document.id.in_(doc_ids)).all()
        
        # Extract data
        results = []
        for doc in documents:
            # Get all pages for this document
            pages = Page.query.filter_by(document_id=doc.id).all()
            
            # Prepare document content
            doc_content = {
                'id': doc.id,
                'name': doc.filename,
                'pages': {page.page_number: page.content for page in pages}
            }
            
            # Extract data using rules
            doc_results = pattern_extractor.extract_from_document(doc_content, rules)
            results.extend(doc_results)
        
        # Clear session data
        session.pop('extraction_rules', None)
        session.pop('document_ids', None)
        
        return render_template('results.html', results=results)
    except Exception as e:
        logger.error(f"Error extracting data: {str(e)}")
        flash(f'Error extracting data: {str(e)}', 'error')
        return redirect(url_for('extract_data'))


@app.route('/document/<int:doc_id>')
def view_document(doc_id):
    """View a specific document"""
    document = Document.query.get_or_404(doc_id)
    pages = Page.query.filter_by(document_id=doc_id).order_by(Page.page_number).all()
    return render_template('document.html', document=document, pages=pages)


@app.route('/document/<int:doc_id>/delete', methods=['POST'])
def delete_document(doc_id):
    """Delete a document"""
    document = Document.query.get_or_404(doc_id)
    
    try:
        # Delete associated pages
        Page.query.filter_by(document_id=doc_id).delete()
        
        # Delete the document
        db.session.delete(document)
        db.session.commit()
        
        flash(f'Document "{document.filename}" deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting document: {str(e)}")
        flash(f'Error deleting document: {str(e)}', 'error')
    
    return redirect(url_for('list_documents'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
