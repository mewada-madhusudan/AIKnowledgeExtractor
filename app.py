import os
import tempfile
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix

from database import db
from models import Document, Page, ExtractionRule, ExtractionResult
from processors.document_processor import DocumentProcessor
from processors.pdf_processor import PDFProcessor
from processors.docx_processor import DocxProcessor
from processors.image_processor import ImageProcessor
from extractors.pattern_extractor import PatternExtractor

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SESSION_SECRET", "development-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'docprocessor.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'doc_processor_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'jpeg', 'png'}

# Initialize processors
document_processor = DocumentProcessor([
    PDFProcessor(),
    DocxProcessor(),
    ImageProcessor()
])

# Initialize extractors
pattern_extractor = PatternExtractor()


# Helper function to check allowed file extensions
def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Create database tables
with app.app_context():
    db.create_all()


# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/documents')
def list_documents():
    """List all processed documents"""
    documents = Document.query.order_by(Document.created_at.desc()).all()
    return render_template('documents.html', documents=documents)


@app.route('/documents', methods=['POST'])
def upload_document():
    """Handle document upload and processing"""
    if 'document' not in request.files:
        flash('No document part', 'danger')
        return redirect(request.url)
    
    file = request.files['document']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            document_id, page_count = document_processor.process(file_path, filename)
            flash(f'Document uploaded and processed successfully. {page_count} pages extracted.', 'success')
            return redirect(url_for('view_document', doc_id=document_id))
        except Exception as e:
            flash(f'Error processing document: {str(e)}', 'danger')
            return redirect(url_for('list_documents'))
    else:
        flash('File type not allowed. Please upload PDF, DOCX, or image files.', 'warning')
        return redirect(request.url)


@app.route('/extract')
def extract_data():
    """Handle extraction request"""
    documents = Document.query.order_by(Document.created_at.desc()).all()
    return render_template('extract.html', documents=documents)


@app.route('/results', methods=['POST'])
def show_results():
    """Show extraction results"""
    if 'document_ids' not in request.form:
        flash('No documents selected', 'warning')
        return redirect(url_for('extract_data'))
    
    if 'excel_file' not in request.files:
        flash('No Excel file uploaded', 'warning')
        return redirect(url_for('extract_data'))
    
    excel_file = request.files['excel_file']
    
    if excel_file.filename == '':
        flash('No selected Excel file', 'warning')
        return redirect(url_for('extract_data'))
    
    # Save Excel file temporarily
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(excel_file.filename))
    excel_file.save(excel_path)
    
    # Load extraction rules from Excel
    rules = pattern_extractor.load_rules_from_excel(excel_path)
    
    if not rules:
        flash('No valid extraction rules found in Excel file', 'warning')
        return redirect(url_for('extract_data'))
    
    # Save rules to database
    saved_rules = []
    for rule in rules:
        db_rule = ExtractionRule(
            name=rule.get('field_name', 'Unnamed Field'),
            pattern=rule.get('search_pattern', ''),
            extraction_type=rule.get('extraction_type', 'exact'),
            context=rule.get('context_before', '') + ' | ' + rule.get('context_after', ''),
            instructions=rule.get('instructions', '')
        )
        db.session.add(db_rule)
        saved_rules.append(db_rule)
    
    db.session.commit()
    
    # Extract data from selected documents
    document_ids = request.form.getlist('document_ids')
    results = []
    
    for doc_id in document_ids:
        document = Document.query.get(doc_id)
        if document:
            # Create document object for the extractor
            doc_data = {
                'id': document.id,
                'filename': document.filename,
                'file_type': document.file_type,
                'pages': {}
            }
            
            # Add page content
            for page in document.pages:
                doc_data['pages'][page.page_number] = page.content
            
            # Extract data using rules
            extraction_results = pattern_extractor.extract_from_document(doc_data, rules)
            
            # Save results to database
            for result in extraction_results:
                rule_index = result.get('rule_index', 0)
                if rule_index < len(saved_rules):
                    db_result = ExtractionResult(
                        document_id=document.id,
                        rule_id=saved_rules[rule_index].id,
                        page_number=result.get('page_number', 1),
                        value=result.get('value', ''),
                        context=result.get('context', '')
                    )
                    db.session.add(db_result)
                    results.append(db_result)
    
    db.session.commit()
    
    # Get all results with related data
    all_results = ExtractionResult.query.filter(
        ExtractionResult.id.in_([r.id for r in results])
    ).order_by(
        ExtractionResult.document_id,
        ExtractionResult.page_number
    ).all()
    
    return render_template('results.html', 
                          results=all_results, 
                          rules=saved_rules,
                          document_count=len(set(r.document_id for r in results)))


@app.route('/documents/<int:doc_id>')
def view_document(doc_id):
    """View a specific document"""
    document = Document.query.get_or_404(doc_id)
    pages = Page.query.filter_by(document_id=doc_id).order_by(Page.page_number).all()
    return render_template('document.html', document=document, pages=pages)


@app.route('/documents/<int:doc_id>/delete', methods=['POST'])
def delete_document(doc_id):
    """Delete a document"""
    document = Document.query.get_or_404(doc_id)
    
    try:
        db.session.delete(document)
        db.session.commit()
        flash(f'Document "{document.filename}" deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting document: {str(e)}', 'danger')
    
    return redirect(url_for('list_documents'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)