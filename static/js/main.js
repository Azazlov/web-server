/**
 * FileShare Local v2.1 - Enhanced JavaScript
 * Modern animations and improved interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all enhancements
    initAlerts();
    initDeleteConfirmation();
    initFilePreview();
    initKeyboardShortcuts();
    initTooltips();
    initPopovers();
    initTableInteractions();
    initUploadProgress();
    initNavbarScroll();
    initAnimations();
    initRippleEffect();
    initDragDropUpload();
    
    console.log('%c📁 FileShare Local v2.1 Enhanced UI initialized', 'color: #667eea; font-size: 14px; font-weight: bold;');
});

/**
 * Auto-dismiss alerts with smooth animation
 */
function initAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert, index) {
        // Stagger animation
        alert.style.animationDelay = `${index * 0.1}s`;
        
        setTimeout(function() {
            alert.classList.add('fade');
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}

/**
 * Enhanced delete confirmation with custom styling
 */
function initDeleteConfirmation() {
    const deleteButtons = document.querySelectorAll('form[onsubmit*="confirm"]');
    deleteButtons.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const message = form.getAttribute('onsubmit').match(/confirm\('(.*)'\)/);
            if (message && message[1]) {
                e.preventDefault();
                showConfirmDialog(message[1])
                    .then(confirmed => {
                        if (confirmed) {
                            form.submit();
                        }
                    });
            }
        });
    });
}

/**
 * Custom confirmation dialog
 */
function showConfirmDialog(message) {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            backdrop-filter: blur(5px);
            animation: fadeIn 0.2s ease-out;
        `;
        
        const dialog = document.createElement('div');
        dialog.style.cssText = `
            background: white;
            border-radius: 16px;
            padding: 30px;
            max-width: 400px;
            margin: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: slideInDown 0.3s ease-out;
        `;
        
        dialog.innerHTML = `
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 15px;">⚠️</div>
                <h4 style="margin-bottom: 15px; color: #2d3748;">Подтверждение</h4>
                <p style="color: #718096; margin-bottom: 25px;">${message}</p>
                <div style="display: flex; gap: 12px; justify-content: center;">
                    <button class="btn-cancel" style="
                        padding: 10px 24px;
                        border: 2px solid #e2e8f0;
                        background: white;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: 500;
                        transition: all 0.2s;
                    ">Отмена</button>
                    <button class="btn-confirm" style="
                        padding: 10px 24px;
                        border: none;
                        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                        color: white;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: 500;
                        box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
                        transition: all 0.2s;
                    ">Подтвердить</button>
                </div>
            </div>
        `;
        
        overlay.appendChild(dialog);
        document.body.appendChild(overlay);
        
        const btnCancel = dialog.querySelector('.btn-cancel');
        const btnConfirm = dialog.querySelector('.btn-confirm');
        
        function cleanup() {
            overlay.style.opacity = '0';
            setTimeout(() => overlay.remove(), 200);
        }
        
        btnCancel.addEventListener('click', () => {
            cleanup();
            resolve(false);
        });
        
        btnConfirm.addEventListener('click', () => {
            cleanup();
            resolve(true);
        });
        
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                cleanup();
                resolve(false);
            }
        });
    });
}

/**
 * File input with preview
 */
function initFilePreview() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                const fileName = file.name;

                // Show visual feedback
                input.parentElement.classList.add('file-selected');

                // Create or update preview
                let preview = input.parentElement.querySelector('.file-preview');
                if (!preview) {
                    preview = document.createElement('div');
                    preview.className = 'file-preview';
                    preview.style.cssText = `
                        margin-top: 10px;
                        padding: 12px;
                        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                        border-radius: 8px;
                        border-left: 3px solid #667eea;
                        animation: slideInRight 0.3s ease-out;
                    `;
                    input.parentElement.appendChild(preview);
                }

                preview.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <i class="bi bi-file-earmark-check" style="color: #28a745; font-size: 1.5rem;"></i>
                        <div>
                            <div style="font-weight: 500; color: #2d3748;">${fileName}</div>
                            <div style="font-size: 0.85rem; color: #718096;">${sizeMB} MB</div>
                        </div>
                    </div>
                `;
            }
        });
    });
}

/**
 * Open file preview modal
 */
function openPreview(folderType, filename, relPath) {
    const modal = new bootstrap.Modal(document.getElementById('previewModal'));
    const titleEl = document.getElementById('previewFilename');
    const bodyEl = document.getElementById('previewBody');
    const downloadBtn = document.getElementById('previewDownloadBtn');

    // Build URLs
    const previewUrl = `/preview?folder_type=${encodeURIComponent(folderType)}&filename=${encodeURIComponent(filename)}&path=${encodeURIComponent(relPath)}`;
    const downloadUrl = `/download?folder_type=${encodeURIComponent(folderType)}&filename=${encodeURIComponent(filename)}&path=${encodeURIComponent(relPath)}`;

    titleEl.textContent = filename;
    downloadBtn.href = downloadUrl;
    bodyEl.innerHTML = `
        <div class="d-flex align-items-center justify-content-center" style="height: 400px;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
            </div>
        </div>
    `;

    modal.show();

    // Determine preview type by extension
    const ext = filename.split('.').pop().toLowerCase();
    const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico', 'tiff', 'tif'];
    const textExts = ['txt', 'md', 'csv', 'json', 'xml', 'html', 'htm', 'css', 'js', 'py',
                      'java', 'c', 'cpp', 'h', 'rb', 'go', 'rs', 'ts', 'yaml', 'yml', 'ini',
                      'cfg', 'conf', 'log', 'sh', 'bat', 'sql', 'r', 'm'];

    if (imageExts.includes(ext)) {
        bodyEl.innerHTML = `<img src="${previewUrl}" alt="${filename}" class="img-fluid" style="max-height: 80vh; object-fit: contain; border-radius: 8px;">`;
    } else if (ext === 'pdf') {
        bodyEl.innerHTML = `<iframe src="${previewUrl}" style="width: 100%; height: 80vh; border: none; border-radius: 8px;"></iframe>`;
    } else if (textExts.includes(ext)) {
        // Fetch text content and display with syntax highlighting fallback
        fetch(previewUrl)
            .then(res => {
                if (!res.ok) throw new Error('Network error');
                return res.text();
            })
            .then(text => {
                bodyEl.innerHTML = `
                    <div style="text-align: left; max-height: 70vh; overflow: auto; background: #1e1e1e; border-radius: 8px; padding: 20px;">
                        <pre style="margin: 0; color: #d4d4d4; font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; font-size: 0.85rem; white-space: pre-wrap; word-break: break-word;"><code>${escapeHtml(text)}</code></pre>
                    </div>
                `;
            })
            .catch(err => {
                bodyEl.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle"></i> Ошибка загрузки файла: ${err.message}
                    </div>
                `;
            });
    } else {
        // Generic iframe preview
        bodyEl.innerHTML = `<iframe src="${previewUrl}" style="width: 100%; height: 80vh; border: none; border-radius: 8px;"></iframe>`;
    }
}

/**
 * Escape HTML to prevent XSS in text preview
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Open rename modal with pre-filled values
 */
function openRenameModal(oldName, isDir, folderType) {
    const renameOldName = document.getElementById('renameOldName');
    const renameNewName = document.getElementById('renameNewName');
    const renameIsDir = document.getElementById('renameIsDir');
    const renameFolderType = document.getElementById('renameFolderType');

    renameOldName.value = oldName;
    renameNewName.value = oldName;
    renameIsDir.value = isDir ? 'true' : 'false';
    renameFolderType.value = folderType;

    const modal = new bootstrap.Modal(document.getElementById('renameModal'));
    modal.show();

    // Focus and select the input field
    setTimeout(() => {
        renameNewName.focus();
        // Select only the name part (before extension for files)
        if (!isDir && oldName.includes('.')) {
            const namePart = oldName.substring(0, oldName.lastIndexOf('.'));
            renameNewName.setSelectionRange(0, namePart.length);
        } else {
            renameNewName.select();
        }
    }, 300);
}

/**
 * Enhanced keyboard shortcuts with visual feedback
 */
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+U - Upload focus
        if (e.ctrlKey && e.key === 'u') {
            e.preventDefault();
            const fileInput = document.querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.click();
                showToast('📁 Выберите файл для загрузки', 'info');
            }
        }

        // Ctrl+N - New folder
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            const mkdirModal = document.getElementById('mkdirModal');
            if (mkdirModal) {
                const modal = bootstrap.Modal.getInstance(mkdirModal) || new bootstrap.Modal(mkdirModal);
                modal.show();
            }
        }

        // Escape - Close modals with animation
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(function(modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
}

/**
 * Initialize Bootstrap tooltips with enhanced styling
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            animation: true,
            template: `
                <div class="tooltip" role="tooltip">
                    <div class="tooltip-arrow"></div>
                    <div class="tooltip-inner" style="background: #2d3748; padding: 8px 14px; border-radius: 8px;"></div>
                </div>
            `
        });
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            animation: true,
            trigger: 'hover focus'
        });
    });
}

/**
 * Enhanced table row interactions
 */
function initTableInteractions() {
    const tableRows = document.querySelectorAll('.table-hover tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on buttons or links
            if (e.target.closest('a, button, form')) return;
            
            // Remove active class from all rows
            tableRows.forEach(function(r) {
                r.classList.remove('table-active');
                r.style.background = '';
            });
            
            // Add active class to clicked row
            row.classList.add('table-active');
        });
        
        // Add hover effect
        row.addEventListener('mouseenter', function() {
            row.style.cursor = 'pointer';
        });
    });
}

/**
 * Upload progress with animation
 */
function initUploadProgress() {
    const uploadForms = document.querySelectorAll('form[enctype="multipart/form-data"]');
    uploadForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalContent = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    <span>Загрузка...</span>
                `;
                submitBtn.style.opacity = '0.7';
                
                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalContent;
                    submitBtn.style.opacity = '1';
                }, 10000);
            }
        });
    });
}

/**
 * Navbar scroll effect
 */
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    let lastScroll = 0;
    
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });
}

/**
 * Initialize entrance animations
 */
function initAnimations() {
    // Animate cards on scroll
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `all 0.5s ease ${index * 0.1}s`;
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + index * 100);
    });
    
    // Animate table rows
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';
        row.style.transition = `all 0.3s ease ${index * 0.05}s`;
        
        setTimeout(() => {
            row.style.opacity = '1';
            row.style.transform = 'translateX(0)';
        }, 300 + index * 50);
    });
}

/**
 * Ripple effect for buttons
 */
function initRippleEffect() {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.4);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;
            
            button.style.position = 'relative';
            button.style.overflow = 'hidden';
            button.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    // Add ripple animation
    if (!document.querySelector('#ripple-style')) {
        const style = document.createElement('style');
        style.id = 'ripple-style';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Drag and drop upload support
 */
function initDragDropUpload() {
    const uploadAreas = document.querySelectorAll('.upload-area');
    uploadAreas.forEach(area => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            area.addEventListener(eventName, () => {
                area.classList.add('drag-over');
                area.style.borderColor = '#667eea';
                area.style.background = 'linear-gradient(135deg, #ebf5fb 0%, #e2e8f0 100%)';
                area.style.transform = 'scale(1.02)';
            });
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, () => {
                area.classList.remove('drag-over');
                area.style.borderColor = '';
                area.style.background = '';
                area.style.transform = '';
            });
        });
        
        area.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                const fileInput = area.querySelector('input[type="file"]');
                if (fileInput) {
                    fileInput.files = files;
                    // Trigger change event
                    const event = new Event('change');
                    fileInput.dispatchEvent(event);
                }
            }
        });
    });
}

/**
 * Show toast notification with enhanced styling
 */
function showToast(message, type = 'info') {
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    const bgColors = {
        success: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
        error: 'linear-gradient(135deg, #dc3545 0%, #e83e8c 100%)',
        warning: 'linear-gradient(135deg, #ffc107 0%, #fd7e14 100%)',
        info: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    };

    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white border-0';
    toast.style.cssText = `
        background: ${bgColors[type] || bgColors.info};
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        border-radius: 12px;
        animation: slideInRight 0.3s ease-out;
    `;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body" style="font-weight: 500;">
                ${icons[type] || icons.info} ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" style="opacity: 0.8;"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 4000 });
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', function() {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    });
}

/**
 * Format file size to human-readable format
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
 * Smooth scroll to element
 */
function scrollToElement(element, offset = 0) {
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
    const offsetPosition = elementPosition - offset;
    
    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

/**
 * Copy to clipboard with feedback
 */
function copyToClipboard(text, message = 'Скопировано!') {
    navigator.clipboard.writeText(text).then(() => {
        showToast(message, 'success');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast(message, 'success');
    });
}

// Add CSS animations for dynamic elements
const dynamicStyles = document.createElement('style');
dynamicStyles.textContent = `
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;
document.head.appendChild(dynamicStyles);
