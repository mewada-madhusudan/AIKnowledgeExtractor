// Main JavaScript for AI Document Processor

// Toggle select all documents in extraction page
function toggleSelectAll() {
    const checkboxes = document.querySelectorAll('.document-checkbox');
    const anyUnchecked = Array.from(checkboxes).some(cb => !cb.checked);
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = anyUnchecked;
    });
    
    updateSelectedCount();
}

// Update selected documents count
function updateSelectedCount() {
    const count = document.querySelectorAll('.document-checkbox:checked').length;
    const countElement = document.getElementById('selectedCount');
    if (countElement) {
        countElement.textContent = count + ' document' + (count !== 1 ? 's' : '') + ' selected';
    }
    
    const errorElement = document.getElementById('documentSelectionError');
    if (errorElement) {
        errorElement.classList.add('d-none');
    }
}

// Toggle page content visibility
function togglePageContent(pageId) {
    const content = document.getElementById(`page-content-${pageId}`);
    const button = document.getElementById(`toggle-btn-${pageId}`);
    
    if (content.classList.contains('d-none')) {
        content.classList.remove('d-none');
        button.innerHTML = '<i class="fas fa-minus-circle"></i> Hide Content';
    } else {
        content.classList.add('d-none');
        button.innerHTML = '<i class="fas fa-plus-circle"></i> Show Content';
    }
}

// Export results to CSV
function exportToCSV() {
    const table = document.getElementById('resultsTable');
    if (!table) return;
    
    // Create CSV content
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const row = [], cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
            // Skip the context column (which is interactive)
            if (j === 4 && i > 0) { 
                const contextDiv = cols[j].querySelector('div.collapse');
                const preEl = contextDiv ? contextDiv.querySelector('pre') : null;
                const contextText = preEl ? preEl.textContent.trim() : '';
                
                // Escape quotes and handle CSV format
                let cell = contextText.replace(/"/g, '""');
                if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) {
                    cell = `"${cell}"`;
                }
                row.push(cell);
            } else if (j !== 4 || i === 0) {
                // Get content from regular cells
                let cell = cols[j].innerText.trim();
                
                // Escape quotes and handle CSV format
                cell = cell.replace(/"/g, '""');
                if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) {
                    cell = `"${cell}"`;
                }
                row.push(cell);
            }
        }
        csv.push(row.join(','));
    }
    
    // Download CSV file
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'extraction_results.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Preview document before uploading
function previewDocument() {
    const fileInput = document.getElementById('document');
    const previewContainer = document.getElementById('document-preview');
    
    if (fileInput.files && fileInput.files[0]) {
        const file = fileInput.files[0];
        const filename = file.name;
        const filesize = (file.size / 1024).toFixed(2) + ' KB';
        const filetype = file.type;
        
        let iconClass = 'far fa-file';
        if (file.type.includes('pdf')) {
            iconClass = 'far fa-file-pdf';
        } else if (file.type.includes('word') || filename.endsWith('.docx')) {
            iconClass = 'far fa-file-word';
        } else if (file.type.includes('image')) {
            iconClass = 'far fa-file-image';
        }
        
        previewContainer.innerHTML = `
            <div class="card bg-light mb-3">
                <div class="card-body">
                    <h5 class="card-title">
                        <i class="${iconClass} me-2"></i>
                        ${filename}
                    </h5>
                    <p class="card-text">
                        <small>Type: ${filetype}</small><br>
                        <small>Size: ${filesize}</small>
                    </p>
                </div>
            </div>
        `;
        previewContainer.classList.remove('d-none');
    } else {
        previewContainer.classList.add('d-none');
    }
}