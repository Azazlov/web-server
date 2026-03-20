/**
 * FileShare Local v2.1 - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete actions
    const deleteForms = document.querySelectorAll('form[onsubmit*="confirm"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const message = form.getAttribute('onsubmit').match(/confirm\('(.*)'\)/);
            if (message && message[1]) {
                if (!confirm(message[1])) {
                    e.preventDefault();
                }
            }
        });
    });

    // File input preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const sizeMB = file.size / (1024 * 1024);
                console.log(`Selected file: ${file.name} (${sizeMB.toFixed(2)} MB)`);
            }
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+U - Upload focus
        if (e.ctrlKey && e.key === 'u') {
            e.preventDefault();
            const fileInput = document.querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.click();
            }
        }
        
        // Ctrl+N - New folder
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            const mkdirBtn = document.querySelector('[data-bs-target="#mkdirModal"]');
            if (mkdirBtn) {
                const modal = new bootstrap.Modal(document.getElementById('mkdirModal'));
                modal.show();
            }
        }
        
        // Escape - Close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(function(modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });

    // Tooltip initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Popover initialization
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Table row click to select (optional feature)
    const tableRows = document.querySelectorAll('.table-hover tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('click', function() {
            // Remove active class from all rows
            tableRows.forEach(function(r) {
                r.classList.remove('table-active');
            });
            // Add active class to clicked row
            row.classList.add('table-active');
        });
    });

    // Upload progress indicator (if needed in future)
    const uploadForms = document.querySelectorAll('form enctype="multipart/form-data"]');
    uploadForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Загрузка...';
            }
        });
    });

    console.log('FileShare Local initialized');
});

/**
 * Format file size to human-readable format
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Format date to local format
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date
 */
function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type: success, error, warning, info
 */
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        // Create container if not exists
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.querySelector('.toast-container').appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove after hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}
