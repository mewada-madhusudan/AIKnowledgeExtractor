import pandas as pd

# Create a sample Excel file with extraction rules
data = {
    'field_name': [
        'Invoice Number', 
        'Total Amount', 
        'Customer Name', 
        'Shipping Address', 
        'Order Date',
        'Product Description'
    ],
    'search_pattern': [
        'Invoice #', 
        'Total:', 
        'Bill To:', 
        '', 
        '',
        ''
    ],
    'extraction_type': [
        'after_pattern', 
        'after_pattern', 
        'after_pattern', 
        'nlp', 
        'nlp',
        'nlp'
    ],
    'instructions': [
        'Extract text after Invoice # pattern', 
        'Extract total amount from the invoice', 
        'Extract customer name from billing information', 
        'Find the full shipping address, including street, city, state and zip code', 
        'Extract the date when the order was placed',
        'Extract detailed description of the product including model number and specifications'
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel file
df.to_excel('static/sample_extraction_rules.xlsx', index=False)
print('Sample Excel file created: static/sample_extraction_rules.xlsx')