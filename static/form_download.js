// Enhanced form download functionality
// This file provides actual API integration for PDF and DOCX downloads

// Enhanced form data collection that captures current form state including company name
function collectFormData() {
    const formData = {};
    const form = document.getElementById('dynamicForm');
    
    if (!form) {
        return formData;
    }
    
    // Get all form inputs
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        if (input.type === 'checkbox' || input.type === 'radio') {
            if (input.checked) {
                const name = input.name.replace('[]', '');
                if (!formData[name]) {
                    formData[name] = [];
                }
                if (Array.isArray(formData[name])) {
                    formData[name].push(input.value);
                } else {
                    formData[name] = input.value;
                }
            }
        } else if (input.value && input.value.trim() !== '') {
            formData[input.name] = input.value;
        }
    });
    
    return formData;
}

// Function to get current company name from the page
function getCurrentCompanyName() {
    // Try multiple selectors to find company name
    const selectors = [
        '.company-name',
        '[data-company]',
        'h2:contains("Corporation")',
        'h2:contains("Company")',
        'h2:contains("Inc")',
        'h2:contains("LLC")'
    ];
    
    for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element && element.textContent.trim()) {
            return element.textContent.trim();
        }
        // Also check data attributes
        if (element && element.dataset.company) {
            return element.dataset.company;
        }
    }
    
    // Fallback: look for any text that might be a company name
    const headings = document.querySelectorAll('h1, h2, h3, .form-title');
    for (const heading of headings) {
        const text = heading.textContent.trim();
        if (text.includes('Corporation') || text.includes('Company') || 
            text.includes('Inc') || text.includes('LLC') || text.includes('Ltd')) {
            return text;
        }
    }
    
    return 'Your Company'; // Default fallback
}

// Function to update company name in the HTML before download
function updateCompanyNameInHTML(htmlContent, newCompanyName) {
    if (!newCompanyName || newCompanyName === 'Your Company') {
        return htmlContent;
    }
    
    // Replace various patterns of company name in the HTML
    const patterns = [
        /<div[^>]*class="[^"]*company-name[^>]*>([^<]+)<\/div>/gi,
        /<span[^>]*class="[^"]*company-name[^>]*>([^<]+)<\/span>/gi,
        /<h2[^>]*>([^<]*Company[^<]*)<\/h2>/gi,
        /Your Company/gi
    ];
    
    let updatedHTML = htmlContent;
    patterns.forEach(pattern => {
        updatedHTML = updatedHTML.replace(pattern, (match, group1) => {
            return match.replace(group1 || 'Your Company', newCompanyName);
        });
    });
    
    return updatedHTML;
}

function downloadAsPDF() {
    const formData = collectFormData();
    
    // Show loading indicator
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating PDF...';
    btn.disabled = true;
    
    // Get the complete HTML content
    let htmlContent = document.documentElement.outerHTML;
    
    // Get current company name and update HTML if needed
    const currentCompanyName = getCurrentCompanyName();
    htmlContent = updateCompanyNameInHTML(htmlContent, currentCompanyName);
    
    // Extract form title from the page
    const formTitle = document.querySelector('.form-title')?.textContent || 'form';
    const filename = formTitle.replace(/\s+/g, '_').toLowerCase();
    
    console.log('Downloading PDF with company name:', currentCompanyName);
    
    // Make API call to convert form to PDF
    fetch('/api/convert-form', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            htmlContent: htmlContent,
            filename: filename,
            format: 'pdf'
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();
    })
    .then(blob => {
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${filename}_completed.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        alert('PDF downloaded successfully!');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error generating PDF: ' + error.message);
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

function downloadAsDOCX() {
    const formData = collectFormData();
    
    // Show loading indicator
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating DOCX...';
    btn.disabled = true;
    
    // Get the complete HTML content
    let htmlContent = document.documentElement.outerHTML;
    
    // Get current company name and update HTML if needed
    const currentCompanyName = getCurrentCompanyName();
    htmlContent = updateCompanyNameInHTML(htmlContent, currentCompanyName);
    
    // Extract form title from the page
    const formTitle = document.querySelector('.form-title')?.textContent || 'form';
    const filename = formTitle.replace(/\s+/g, '_').toLowerCase();
    
    console.log('Downloading DOCX with company name:', currentCompanyName);
    
    // Make API call to convert form to DOCX
    fetch('/api/convert-form', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            htmlContent: htmlContent,
            filename: filename,
            format: 'docx'
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();
    })
    .then(blob => {
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${filename}_completed.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        alert('DOCX downloaded successfully!');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error generating DOCX: ' + error.message);
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

// Missing clearForm function
function clearForm() {
    if (confirm('Are you sure you want to clear all form data?\n\nThis action cannot be undone and will remove all entered information.')) {
        const form = document.getElementById('dynamicForm');
        if (form) {
            form.reset();
        }
        
        // Clear localStorage
        localStorage.removeItem('form_progress_' + window.location.pathname);
        
        // Update progress if function exists
        if (typeof updateProgress === 'function') {
            updateProgress();
        }
        
        alert('Form data cleared successfully.');
    }
}

// Missing saveProgress function
function saveProgress() {
    const formData = collectFormData();
    const progressKey = 'form_progress_' + window.location.pathname;
    
    try {
        localStorage.setItem(progressKey, JSON.stringify({
            data: formData,
            timestamp: new Date().toISOString(),
            url: window.location.href
        }));
        
        alert('Progress saved successfully!');
    } catch (error) {
        console.error('Error saving progress:', error);
        alert('Error saving progress. Please try again.');
    }
}

// Missing updateProgress function
function updateProgress() {
    const form = document.getElementById('dynamicForm');
    if (!form) return;
    
    const totalFields = form.querySelectorAll('input, select, textarea').length;
    const filledFields = form.querySelectorAll('input:not([value=""]), select:not([value=""]), textarea:not(:empty)').length;
    
    const percentage = totalFields > 0 ? Math.round((filledFields / totalFields) * 100) : 0;
    
    const progressPercent = document.getElementById('progress-percent');
    const progressFill = document.getElementById('progress-fill');
    
    if (progressPercent) {
        progressPercent.textContent = percentage + '%';
    }
    
    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }
}

// Auto-save functionality
let autoSaveInterval;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Restore saved progress
    const progressKey = 'form_progress_' + window.location.pathname;
    const savedData = localStorage.getItem(progressKey);
    
    if (savedData) {
        try {
            const progress = JSON.parse(savedData);
            const form = document.getElementById('dynamicForm');
            
            if (form && progress.data) {
                // Restore form data
                Object.keys(progress.data).forEach(name => {
                    const field = form.querySelector(`[name="${name}"]`);
                    if (field) {
                        if (field.type === 'checkbox' || field.type === 'radio') {
                            if (Array.isArray(progress.data[name])) {
                                progress.data[name].forEach(value => {
                                    const specificField = form.querySelector(`[name="${name}"][value="${value}"]`);
                                    if (specificField) specificField.checked = true;
                                });
                            } else {
                                const specificField = form.querySelector(`[name="${name}"][value="${progress.data[name]}"]`);
                                if (specificField) specificField.checked = true;
                            }
                        } else {
                            field.value = progress.data[name];
                        }
                    }
                });
                
                updateProgress();
            }
        } catch (error) {
            console.error('Error restoring progress:', error);
        }
    }
    
    // Set up auto-save
    const form = document.getElementById('dynamicForm');
    if (form) {
        form.addEventListener('input', function() {
            updateProgress();
            
            // Debounced auto-save
            clearTimeout(autoSaveInterval);
            autoSaveInterval = setTimeout(() => {
                const formData = collectFormData();
                if (Object.keys(formData).length > 0) {
                    localStorage.setItem(progressKey, JSON.stringify({
                        data: formData,
                        timestamp: new Date().toISOString(),
                        url: window.location.href
                    }));
                }
            }, 2000); // Save after 2 seconds of inactivity
        });
        
        // Initial progress update
        updateProgress();
    }
});