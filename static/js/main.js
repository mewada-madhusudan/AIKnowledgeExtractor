// Main JS for AI Document Processor

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Initialize document selection counter if on extract page
    if (document.getElementById('selected-count')) {
        updateSelectedCount();
    }
});

// Toggle selection of all documents
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('select-all');
    const documentCheckboxes = document.querySelectorAll('.document-checkbox');
    
    documentCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
    
    updateSelectedCount();
}

// Update the selected documents count
function updateSelectedCount() {
    const selectedCheckboxes = document.querySelectorAll('.document-checkbox:checked');
    const selectedCount = document.getElementById('selected-count');
    const extractButton = document.getElementById('extract-button');
    
    if (selectedCount) {
        selectedCount.textContent = selectedCheckboxes.length;
    }
    
    if (extractButton) {
        if (selectedCheckboxes.length > 0) {
            extractButton.disabled = false;
        } else {
            extractButton.disabled = true;
        }
    }
}

// Toggle page content visibility
function togglePageContent(pageId) {
    // This is used for lazy loading or other functionality
    console.log('Toggle page: ' + pageId);
}

// Export results to CSV
function exportToCSV() {
    const table = document.getElementById('results-table');
    if (!table) return;
    
    let csv = [];
    
    // Get headers
    let headers = [];
    const headerCells = table.querySelectorAll('thead th');
    headerCells.forEach(cell => {
        headers.push(cell.textContent.trim());
    });
    csv.push(headers.join(','));
    
    // Get rows
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        let rowData = [];
        const cells = row.querySelectorAll('td');
        
        cells.forEach((cell, index) => {
            // Special handling for first column (field name in badge)
            if (index === 0) {
                const badge = cell.querySelector('.badge');
                if (badge) {
                    rowData.push('"' + badge.textContent.trim() + '"');
                } else {
                    rowData.push('""');
                }
            } 
            // Special handling for links in cells
            else if (cell.querySelector('a')) {
                rowData.push('"' + cell.textContent.trim().replace(/"/g, '""') + '"');
            } 
            // Regular cell content
            else {
                rowData.push('"' + cell.textContent.trim().replace(/"/g, '""') + '"');
            }
        });
        
        csv.push(rowData.join(','));
    });
    
    // Download CSV
    const csvContent = 'data:text/csv;charset=utf-8,' + csv.join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'extraction_results.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Document file preview
function previewDocument() {
    const fileInput = document.getElementById('document');
    const previewContainer = document.getElementById('preview-container');
    const previewIcon = document.getElementById('preview-icon');
    const previewName = document.getElementById('preview-name');
    const previewSize = document.getElementById('preview-size');
    
    if (fileInput && fileInput.files && fileInput.files[0]) {
        const file = fileInput.files[0];
        previewContainer.classList.remove('d-none');
        previewName.textContent = file.name;
        
        // Format file size
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
        previewSize.textContent = `${fileSizeMB} MB`;
        
        // Set appropriate icon
        const extension = file.name.split('.').pop().toLowerCase();
        previewIcon.className = 'fas fa-2x me-3 ';
        
        if (extension === 'pdf') {
            previewIcon.className += 'fa-file-pdf text-danger';
        } else if (extension === 'docx' || extension === 'doc') {
            previewIcon.className += 'fa-file-word text-primary';
        } else if (['jpg', 'jpeg', 'png', 'gif'].includes(extension)) {
            previewIcon.className += 'fa-file-image text-success';
        } else {
            previewIcon.className += 'fa-file text-muted';
        }
    } else if (previewContainer) {
        previewContainer.classList.add('d-none');
    }
}