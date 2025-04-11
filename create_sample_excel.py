"""
Script to create a sample Excel file with extraction rules
"""
import pandas as pd
import os

def create_sample_excel():
    """Create a sample Excel file with various extraction rules"""
    
    # Define the data for the Excel file
    data = {
        'field_name': [
            'Invoice Number',
            'Invoice Date',
            'Total Amount',
            'Company Name',
            'Customer Address',
            'Customer Email',
            'Customer Support',
            'Payment Due Date'
        ],
        'search_pattern': [
            'Invoice #',
            'Invoice Date:',
            'Total:',
            'Company:',
            '',
            'Email:',
            'Phone:',
            ''
        ],
        'extraction_type': [
            'after_pattern',  # Extract text after "Invoice #"
            'after_pattern',  # Extract text after "Invoice Date:"
            'after_pattern',  # Extract text after "Total:"
            'after_pattern',  # Extract text after "Company:"
            'nlp',            # Use NLP to extract address
            'regex',          # Use regex to extract email
            'regex',          # Use regex to extract phone number
            'nlp'             # Use NLP to extract due date
        ],
        'context_before': [
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            ''
        ],
        'context_after': [
            '\n',  # Extract until newline
            '\n',  # Extract until newline
            '\n',  # Extract until newline
            '\n',  # Extract until newline
            '',    # Not used for NLP
            '',    # Not used for regex
            '',    # Not used for regex
            ''     # Not used for NLP
        ],
        'instructions': [
            '',  # Not used for after_pattern
            '',  # Not used for after_pattern
            '',  # Not used for after_pattern
            '',  # Not used for after_pattern
            'Find the complete customer address in the document',  # NLP instruction
            '',  # Not used for regex (using r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
            '',  # Not used for regex (using r'\+\d{1,2}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
            'Extract the payment due date or deadline for payment'  # NLP instruction
        ]
    }
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Create the static directory if it doesn't exist
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Save the DataFrame to an Excel file
    excel_path = os.path.join(static_dir, 'sample_extraction_rules.xlsx')
    df.to_excel(excel_path, index=False)
    
    print(f"Sample Excel file created at: {excel_path}")

if __name__ == "__main__":
    create_sample_excel()