import datetime
from app import db


class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    page_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    pages = db.relationship('Page', backref='document', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Document {self.filename}>'


class Page(db.Model):
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Page {self.page_number} of Document {self.document_id}>'


class ExtractionRule(db.Model):
    __tablename__ = 'extraction_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    pattern = db.Column(db.String(255), nullable=False)
    context = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<ExtractionRule {self.name}>'


class ExtractionResult(db.Model):
    __tablename__ = 'extraction_results'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey('extraction_rules.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Text, nullable=True)
    context = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    rule = db.relationship('ExtractionRule', backref='results')
    document = db.relationship('Document', backref='extraction_results')
    
    def __repr__(self):
        return f'<ExtractionResult for Rule {self.rule_id} from Document {self.document_id}>'
