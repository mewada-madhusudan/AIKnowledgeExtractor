// Document upload preview
function previewDocument() {
  const fileInput = document.getElementById('document-upload');
  const previewContainer = document.getElementById('document-preview');
  const fileNameDisplay = document.getElementById('file-name');
  
  if (fileInput && fileInput.files && fileInput.files[0]) {
    const file = fileInput.files[0];
    
    // Update file name display
    if (fileNameDisplay) {
      fileNameDisplay.textContent = file.name;
    }
    
    // Show preview container
    if (previewContainer) {
      previewContainer.classList.remove('d-none');
    }
    
    // Enable upload button
    const uploadButton = document.getElementById('upload-button');
    if (uploadButton) {
      uploadButton.disabled = false;
    }
  }
}

// Handle document selection for extraction
function updateSelectedCount() {
  const checkboxes = document.querySelectorAll('input[name="document_ids"]:checked');
  const selectedCount = document.getElementById('selected-count');
  
  if (selectedCount) {
    selectedCount.textContent = checkboxes.length;
  }
  
  // Enable/disable extract button based on selection
  const extractButton = document.getElementById('extract-button');
  if (extractButton) {
    extractButton.disabled = checkboxes.length === 0;
  }
}

// Toggle document selection
function toggleSelectAll() {
  const selectAllCheckbox = document.getElementById('select-all');
  const documentCheckboxes = document.querySelectorAll('input[name="document_ids"]');
  
  if (selectAllCheckbox) {
    documentCheckboxes.forEach(checkbox => {
      checkbox.checked = selectAllCheckbox.checked;
    });
    
    updateSelectedCount();
  }
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
  // Initialize Bootstrap tooltips
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
  
  // Initialize Bootstrap popovers
  const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
  const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
  
  // Add event listeners to document checkboxes
  const documentCheckboxes = document.querySelectorAll('input[name="document_ids"]');
  documentCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', updateSelectedCount);
  });
  
  // Add event listener to select all checkbox
  const selectAllCheckbox = document.getElementById('select-all');
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', toggleSelectAll);
  }
  
  // Add event listener to document upload
  const fileInput = document.getElementById('document-upload');
  if (fileInput) {
    fileInput.addEventListener('change', previewDocument);
  }
});

// Show/hide page content
function togglePageContent(pageId) {
  const contentElement = document.getElementById(`page-content-${pageId}`);
  if (contentElement) {
    contentElement.classList.toggle('d-none');
  }
}

// Export results to CSV
function exportToCSV() {
  // Get table data
  const table = document.getElementById('results-table');
  if (!table) return;
  
  const rows = table.querySelectorAll('tr');
  const csvContent = [];
  
  // Add header row
  const headerRow = [];
  const headers = rows[0].querySelectorAll('th');
  headers.forEach(header => {
    headerRow.push(`"${header.textContent.trim()}"`);
  });
  csvContent.push(headerRow.join(','));
  
  // Add data rows
  for (let i = 1; i < rows.length; i++) {
    const dataRow = [];
    const cells = rows[i].querySelectorAll('td');
    cells.forEach(cell => {
      dataRow.push(`"${cell.textContent.trim().replace(/"/g, '""')}"`);
    });
    csvContent.push(dataRow.join(','));
  }
  
  // Create and download CSV file
  const csvString = csvContent.join('\n');
  const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', 'extraction_results.csv');
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
