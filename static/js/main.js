// Global variables
let currentCategories = [];
let originalUrlForPromptModal = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeMasonryLayout();
    initializeImageLoading();
});

// ======================
// GLOBAL TOP LOADER
// ======================
function showTopLoader() {
    document.documentElement.classList.add('top-loader-active');
}
function hideTopLoader() {
    document.documentElement.classList.remove('top-loader-active');
}

// Auto-bind to forms that should show loading
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form.show-loading');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            showTopLoader();
            // Safety timeout to hide after 10s if not redirected
            setTimeout(hideTopLoader, 10000);
        });
    });
});

// Event Listeners
function initializeEventListeners() {
    // Card click events
    document.addEventListener('click', function(e) {
        const promptCard = e.target.closest('.prompt-card');
        const sponsorCard = e.target.closest('.sponsor-card');
        
        if (promptCard && !e.target.closest('.btn, .unsave-btn')) {
            const promptId = promptCard.closest('[data-prompt-id]').dataset.promptId;
            viewPrompt(promptId);
        } else if (sponsorCard && !e.target.closest('.btn')) {
            const sponsorshipId = sponsorCard.closest('[data-sponsorship-id]').dataset.sponsorshipId;
            viewSponsorship(sponsorshipId);
        }
    });

    // Modal events
    const promptModal = document.getElementById('promptModal');
    if (promptModal) {
        promptModal.addEventListener('hidden.bs.modal', function() {
            document.getElementById('promptModalContent').innerHTML = '';
            // Restore original URL if we navigated to a slug while opening modal
            if (originalUrlForPromptModal) {
                history.replaceState({}, '', originalUrlForPromptModal);
                originalUrlForPromptModal = null;
            }
        });
    }

    // Close modal on back button if open
    window.addEventListener('popstate', function() {
        const modalEl = document.getElementById('promptModal');
        if (modalEl && modalEl.classList.contains('show')) {
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            if (modalInstance) modalInstance.hide();
        }
    });

    // Edit modal events
    const editModal = document.getElementById('editPromptModal');
    if (editModal) {
        editModal.addEventListener('shown.bs.modal', function() {
            populateCategorySelect();
        });
    }
}

// Initialize masonry layout (CSS-only approach, but we can add JavaScript enhancements)
function initializeMasonryLayout() {
    // Add any JavaScript enhancements to the CSS masonry layout if needed
    const masonryContainer = document.querySelector('.masonry-container');
    if (masonryContainer) {
        // Force reflow to ensure proper layout
        masonryContainer.style.columnFill = 'balance';
    }
}

// Initialize image loading with lazy loading support
function initializeImageLoading() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    images.forEach(img => {
        img.addEventListener('load', function() {
            this.style.animation = 'none';
        });
        
        img.addEventListener('error', function() {
            this.style.animation = 'none';
            this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNHB4IiBmaWxsPSIjOTk5IiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5JbWFnZSBub3QgZm91bmQ8L3RleHQ+PC9zdmc+';
        });
    });
}

// View prompt details
async function viewPrompt(promptId) {
    try {
        const response = await fetch(`/get_prompt/${promptId}`);
        const data = await response.json();
        
        // Push slug URL to history if available
        if (data.slug) {
            const slugPath = `/prompts/${data.slug}`;
            if (window.location.pathname !== slugPath) {
                originalUrlForPromptModal = window.location.href;
                history.pushState({ modal: 'prompt', slug: data.slug }, '', slugPath);
            }
        }

        showPromptModal(data);
    } catch (error) {
        console.error('Error fetching prompt details:', error);
        showAlert('Error loading prompt details', 'danger');
    }
}

// Show prompt details in modal
function showPromptModal(prompt) {
    const modal = new bootstrap.Modal(document.getElementById('promptModal'));
    const title = document.getElementById('promptModalTitle');
    const content = document.getElementById('promptModalContent');
    
    title.textContent = prompt.title;
    
    // Check if user is authenticated and subscribed
    const isAuthenticated = document.querySelector('.user-info') !== null;
    const isSubscribed = document.querySelector('.badge.bg-success') !== null;
    
    let contentHTML = `
        <div class="row g-4">
            <div class="col-lg-5">
                <div class="prompt-image-container">
                    <img src="${prompt.image_url}" alt="${prompt.title}" class="img-fluid rounded shadow-sm" style="width: 100%; max-height: 500px; object-fit: cover;">
                </div>
            </div>
            <div class="col-lg-7">
                <div class="prompt-details">
                    <div class="detail-section">
                        <h6>${feather.icons['folder'].toSvg()} Category</h6>
                        <p>${prompt.category}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h6>${feather.icons['user'].toSvg()} Creator</h6>
                        <div class="d-flex align-items-center">
                            <a href="/user/${prompt.creator}" class="text-decoration-none d-flex align-items-center">
                                <img src="${prompt.creator_profile_pic || '/static/images/default-profile.svg'}"
                                     alt="${prompt.creator}"
                                     class="rounded-circle me-2"
                                     width="40" height="35"
                                     style="object-fit: cover;">
                                <div>
                                    <div class="text-white">${prompt.creator}</div>
                                    ${prompt.creator_instagram ? `<a href='https://instagram.com/${prompt.creator_instagram}' target='_blank' onclick="event.stopPropagation()"><small class="text-muted">${feather.icons['instagram'].toSvg({width:14,height:14})} @${prompt.creator_instagram}</small></a>` : ''}
                                </div>
                            </a>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h6>${feather.icons['calendar'].toSvg()} Created</h6>
                        <p>${prompt.created_at}</p>
                    </div>
                    
                   <!-- MODELS USED -->
                    <div class="detail-section">
                    <h6 class="text-muted d-flex align-items-center gap-2">
                        ${feather.icons['cpu'].toSvg()} Models Used
                    </h6>

                    <div class="d-flex gap-4 mt-2 flex-wrap justify-content-start align-items-center">
                        <!-- Gemini -->
                        <a href="https://gemini.google.com/" target="_blank" rel="noopener" class="model-item text-center">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/1/1d/Google_Gemini_icon_2025.svg" 
                            alt="Gemini" class="model-icon white-icon"/>
                        <div class="model-name">Gemini</div>
                        </a>

                        <!-- ChatGPT -->
                        <a href="https://chat.openai.com/" target="_blank" rel="noopener" class="model-item text-center">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/e/ef/ChatGPT-Logo.svg" 
                            alt="ChatGPT" class="model-icon white-icon"/>
                        <div class="model-name">ChatGPT</div>
                        </a>

                        <!-- LMArena -->
                        <a href="https://lmarena.ai/" target="_blank" rel="noopener" class="model-item text-center">
                        <img src="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/lmarena-ai-icon.svg" 
                            alt="LMArena" class="model-icon white-icon"/>
                        <div class="model-name">LMArena</div>
                        </a>

                        <!-- MidJourney -->
                        <a href="https://www.midjourney.com/" target="_blank" rel="noopener" class="model-item text-center">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Midjourney_Emblem.svg/960px-Midjourney_Emblem.svg.png?20230928155157
                            alt="MidJourney" class="model-icon white-icon"/>
                        <div class="model-name">MidJourney</div>
                        </a>
                    </div>
                    </div>
                    <!-- END MODELS USED -->
                </div>
            </div>
        </div>
        
        <div class="detail-section mt-3">
            <h6>${feather.icons['info'].toSvg()} Description</h6>
            <p>${prompt.description}</p>
        </div>
    `;
    
    // Show prompt text only for subscribed users (prompt.can_view_details)
    if (prompt.can_view_details) {
        contentHTML += `
            <div class="detail-section">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <!-- Left side: Title -->
                    <h6 class="d-flex align-items-center mb-0">
                        ${feather.icons['file-text'].toSvg()} Prompt Text
                    </h6>

                    <!-- Right side: Buttons -->
                    <div>
                        <button class="btn btn-sm btn-outline-secondary me-1" onclick="copyPromptText('${prompt.id}')" id="copyBtn_${prompt.id}">
                            ${feather.icons['copy'].toSvg()} Copy
                        </button>
                        <button class="btn btn-sm btn-outline-primary" onclick="sharePromptText('${prompt.id}')" id="shareBtn_${prompt.id}">
                            ${feather.icons['share-2'].toSvg()} Share
                        </button>
                    </div>
                </div>
                <p class="font-monospace bg-body-secondary p-3 rounded" id="promptText_${prompt.id}">${prompt.prompt_text}</p>
            </div>
        `;
        
        // Show action buttons for authenticated users
        let actionButtons = '';
        if (!prompt.is_saved) {
            actionButtons += `<button class="btn btn-outline-primary me-2" onclick="savePrompt(this, ${prompt.id})">
                <i class="fa-regular fa-bookmark"></i> Save Prompt
            </button>`;
        } else {
            actionButtons += `<button class="btn btn-outline-secondary me-2" onclick="unsavePrompt(this, ${prompt.id})">
                <i class="fa-solid fa-bookmark"></i> Unsave Prompt
            </button>`;
        }

        
        if (prompt.can_edit) {
            actionButtons += `
                <button class="btn btn-outline-secondary me-2" onclick="editPrompt(${prompt.id})">
                    ${feather.icons['edit'].toSvg()} Edit
                </button>
                <button class="btn btn-outline-danger" onclick="deletePrompt(${prompt.id})">
                    ${feather.icons['trash-2'].toSvg()} Delete
                </button>
            `;
        }
        
        if (actionButtons) {
            contentHTML += `<div class="mt-3">${actionButtons}</div>`;
        }
    } else if (isAuthenticated && !isSubscribed) {
        // Show subscription prompt for non-subscribed users
        contentHTML += `
            <div class="subscription-prompt">
                <div class="icon">🔒</div>
                <h4>Premium Content</h4>
                <p>Upgrade to Premium to view full prompt details and access all features.</p>
                <div class="d-flex gap-2">
                    <form action="/subscription" method="POST" style="display: inline;">
                        <button type="submit" class="btn btn-warning">Upgrade to Premium</button>
                    </form>
                    <!-- Free trial button shown when eligible -->
                    ${prompt.can_start_trial ? `<button id="startTrialBtn" class="btn btn-success">Start 1-month Free Trial</button>` : ''}
                </div>
            </div>
        `;
    } else if (!isAuthenticated ){
        // Show login prompt for non-authenticated users
        contentHTML += `
            <div class="subscription-prompt">
                <div class="icon">🔐</div>
                <h4>Login Required</h4>
                <p>Please login to view full prompt details and access all features.</p>
                <a href="/login" class="btn btn-primary">Login</a>
                <a href="/register" class="btn btn-outline-primary ms-2">Register</a>
            </div>
        `;
    }
    
    content.innerHTML = contentHTML;
    
    // Re-initialize feather icons
    // feather.replace();
    
    modal.show();

    // Wire up free trial button if present
    const trialBtn = document.getElementById('startTrialBtn');
    if (trialBtn) {
        trialBtn.addEventListener('click', async function() {
            try {
                const res = await fetch('/start_trial', { method: 'POST' });
                if (res.redirected) {
                    // If server redirects, follow to update UI
                    window.location.href = res.url;
                    return;
                }

                // Otherwise, try to parse JSON or reload
                window.location.reload();
            } catch (err) {
                console.error('Error starting trial:', err);
                showAlert('Unable to start trial. Please try again.', 'danger');
            }
        });
    }
}

// Edit prompt
async function editPrompt(promptId) {
    try {
        const response = await fetch(`/get_prompt/${promptId}`);
        const data = await response.json();
        
        if (!data.can_edit) {
            showAlert('You can only edit your own prompts', 'danger');
            return;
        }
        
        // Populate the edit form
        document.getElementById('editPromptId').value = promptId;
        document.getElementById('editTitle').value = data.title;
        document.getElementById('editDescription').value = data.description;
        document.getElementById('editPromptText').value = data.prompt_text;
        document.getElementById('editImageUrl').value = data.image_url;
        
        // Show the edit modal
        const modal = new bootstrap.Modal(document.getElementById('editPromptModal'));
        modal.show();
    } catch (error) {
        console.error('Error fetching prompt for edit:', error);
        showAlert('Error loading prompt for editing', 'danger');
    }
}

// Save prompt changes
async function savePromptChanges() {
    const form = document.getElementById('editPromptForm');
    const formData = new FormData(form);
    const promptId = document.getElementById('editPromptId').value;
    
    try {
        const response = await fetch(`/edit_prompt/${promptId}`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('editPromptModal')).hide();
            // Reload the page to show updated content
            window.location.reload();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error saving prompt changes:', error);
        showAlert('Error saving changes', 'danger');
    }
}

// Delete prompt
async function deletePrompt(promptId) {
    const ok = await confirmDialog({ title: 'Delete this prompt?', text: 'This action cannot be undone.', confirmText: 'Delete', icon: 'error' });
    if (!ok) return;
    
    try {
        const response = await fetch(`/delete_prompt/${promptId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message || 'Prompt deleted', 'success');
            // Remove the prompt card from the page
            const promptElement = document.querySelector(`[data-prompt-id="${promptId}"]`);
            if (promptElement) {
                promptElement.remove();
            }
            
            // Close any open modals
            const modals = ['promptModal', 'editPromptModal'];
            modals.forEach(modalId => {
                const modalElement = document.getElementById(modalId);
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }
                }
            });
            window.location.reload();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error deleting prompt:', error);
        showAlert('Error deleting prompt', 'danger');
    }
}

//save prompt
async function savePrompt(button, promptId) {
    try {
        const response = await fetch(`/save_prompt/${promptId}`, { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            showAlert(result.message, 'success');
            button.innerHTML = '<i class="fa-solid fa-bookmark"></i> Unsave Prompt';
            button.className = 'btn btn-outline-secondary me-2';
            button.setAttribute("onclick", `unsavePrompt(this, ${promptId})`);
            // feather.replace();
        } else {
            showAlert(result.message, 'warning');
        }
    } catch (error) {
        console.error('Error saving prompt:', error);
        showAlert('Error saving prompt', 'danger');
    }
}

//unsave prompt
async function unsavePrompt(button, promptId) {
    try {
        const response = await fetch(`/unsave_prompt/${promptId}`, { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            showAlert(result.message, 'success');

            if (window.location.pathname === '/saved_prompts') {
                const promptElement = document.querySelector(`[data-prompt-id="${promptId}"]`);
                if (promptElement) promptElement.remove();
            } else {
                button.innerHTML ='<i class="fa-regular fa-bookmark"></i> Save Prompt';
                button.className = 'btn btn-outline-primary me-2';
                button.setAttribute("onclick", `savePrompt(this, ${promptId})`);
                // feather.replace();
            }
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error unsaving prompt:', error);
        showAlert('Error removing saved prompt', 'danger');
    }
}

// Populate category select in edit modal
async function populateCategorySelect() {
    const select = document.getElementById('editCategory');
    if (!select || select.children.length > 1) return; // Already populated
    
    try {
        // Get categories from the dropdown in the page (if available)
        const categoryDropdown = document.querySelector('.dropdown-menu');
        if (categoryDropdown) {
            const categoryLinks = categoryDropdown.querySelectorAll('.dropdown-item[href*="category="]');
            categoryLinks.forEach(link => {
                const url = new URL(link.href);
                const categoryId = url.searchParams.get('category');
                const categoryName = link.textContent;
                
                if (categoryId && categoryName) {
                    const option = document.createElement('option');
                    option.value = categoryId;
                    option.textContent = categoryName;
                    select.appendChild(option);
                }
            });
        }
    } catch (error) {
        console.error('Error populating category select:', error);
    }
}

// Show alert message (SweetAlert2 toast if available)
function showAlert(message, type = 'info') {
    if (window.Swal && Swal.fire) {
        const icon = (type === 'danger') ? 'error' : (type === 'warning') ? 'warning' : (type === 'success') ? 'success' : 'info';
        Swal.fire({ toast: true, position: 'top-end', icon, title: message, showConfirmButton: false, timer: 2200, timerProgressBar: true });
        return;
    }
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    let alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container';
        alertContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 1050; max-width: 350px;';
        document.body.appendChild(alertContainer);
    }
    alertContainer.appendChild(alert);
    setTimeout(() => { if (alert.parentNode) alert.remove(); }, 5000);
}

// SweetAlert2 confirmation helper
function confirmDialog({ title = 'Are you sure?', text = '', confirmText = 'Yes', cancelText = 'Cancel', icon = 'warning' } = {}) {
    if (window.Swal && Swal.fire) {
        return Swal.fire({ title, text, icon, showCancelButton: true, confirmButtonText: confirmText, cancelButtonText: cancelText, reverseButtons: true })
            .then(result => !!result.isConfirmed);
    }
    return Promise.resolve(window.confirm(text || title));
}

// Utility function to handle form submissions
function handleFormSubmit(formId, callback) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            callback(new FormData(form));
        });
    }
}

// Mobile sidebar toggle
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar && overlay) {
        sidebar.classList.toggle('show');
        overlay.classList.toggle('show');
        
        // Prevent body scroll when sidebar is open
        if (sidebar.classList.contains('show')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }
}

// Close sidebar
function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar && overlay) {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Close sidebar when clicking nav links on mobile
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 768) {
                closeSidebar();
            }
        });
    });
});

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Handle window resize for responsive layout
window.addEventListener('resize', function() {
    // Recalculate masonry layout if needed
    const masonryContainer = document.querySelector('.masonry-container');
    if (masonryContainer) {
        // Force reflow
        masonryContainer.style.columnFill = 'balance';
    }
});

// Copy prompt text function
async function copyPromptText(promptId) {
    const textElement = document.getElementById(`promptText_${promptId}`);
    const copyBtn = document.getElementById(`copyBtn_${promptId}`);
    
    if (textElement) {
        try {
            await navigator.clipboard.writeText(textElement.textContent);
            
            // Update button to show success
            const originalContent = copyBtn.innerHTML;
            copyBtn.innerHTML = feather.icons['check'].toSvg() + " Copied!";
            copyBtn.classList.remove('btn-outline-secondary');
            copyBtn.classList.add('btn-success');
            
            // Replace feather icons
            // feather.replace();
            
            // Reset button after 2 seconds
            setTimeout(() => {
                copyBtn.innerHTML = originalContent;
                copyBtn.classList.remove('btn-success');
                copyBtn.classList.add('btn-outline-secondary');
                // feather.replace();
            }, 2000);
            
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = textElement.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            showAlert('Prompt text copied to clipboard!', 'success');
        }
    }
}

// Share prompt text function
function sharePromptText(promptId) {
    // Pehle prompt data fetch karo
    fetch(`/get_prompt/${promptId}`)
        .then(res => res.json())
        .then(prompt => {
            const shareUrl = prompt.slug ? `${window.location.origin}/prompts/${prompt.slug}` : `${window.location.origin}/?prompt=${promptId}`;
            // Dynamic share text: title + creator
            const shareText = `Title : ${prompt.title}\nby ${prompt.creator}\nCheck it out here: `;

            if (navigator.share) {
                navigator.share({
                    title: prompt.title,
                    text: shareText,
                    url: shareUrl
                }).then(() => console.log('Prompt shared successfully'))
                  .catch(err => console.error('Error sharing:', err));
            } else {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText(shareText)
                    .then(() => Swal.fire({
                        icon: 'success',
                        title: 'Copied!',
                        text: 'Prompt details copied to clipboard!',
                        confirmButtonColor: '#7a5cff',
                        timer: 2000
                    }));
            }
        })
        .catch(err => {
            console.error('Error fetching prompt for share:', err);
            Swal.fire({
                icon: 'error',
                title: 'Share Failed',
                text: 'Unable to share prompt.',
                confirmButtonColor: '#ff4f4f'
            });
        });
}

document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    const promptId = urlParams.get('prompt');
    if (promptId) {
        // Agar prompt param hai, modal open karo
        viewPrompt(promptId);
        return;
    }

    // If landing directly on a slug URL like /prompts/<slug>, auto-open modal
    const slugMatch = window.location.pathname.match(/^\/prompts\/([a-z0-9\-]+)$/);
    if (slugMatch) {
        const slug = slugMatch[1];
        fetch(`/prompts/${slug}`)
            .then(r => r.json())
            .then(data => {
                // Do not set originalUrlForPromptModal here; user navigated directly.
                showPromptModal(data);
            })
            .catch(() => {});
    }
});

// View sponsorship details
function viewSponsorship(sponsorshipId) {
    // Open sponsorship detail page in new tab
    window.location.href=(`/sponsorship/${sponsorshipId}`);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key to close modals
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
});

// ======================
// GALLERY PAGE LOGIC
// ======================

// Validate image URL (only allow http/https)
function isValidImageUrl(url) {
    try {
        const urlObj = new URL(url, window.location.origin);
        return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
        return false;
    }
}

// Open sponsorship detail
function openSponsorshipModal(sponsorshipId) {
    window.location.href = `/sponsorship/${sponsorshipId}`;
}

// Open prompt modal for pixel gallery
function openPromptModal(promptId, slug) {
    const modal = document.getElementById('promptModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalContent = document.getElementById('modalContent');

    if (!modal || !modalTitle || !modalContent) return;

    fetch(`/prompts/${slug}`)
        .then(response => response.json())
        .then(data => {
            modalTitle.textContent = data.title;

            const contentDiv = document.createElement('div');

            // Image
            const imageDiv = document.createElement('div');
            imageDiv.style.marginBottom = '1.5rem';
            const img = document.createElement('img');
            img.src = isValidImageUrl(data.image_url) ? data.image_url : '/static/images/placeholder.png';
            img.alt = data.title;
            img.style.width = '100%';
            img.style.borderRadius = '8px';
            img.style.border = '2px solid var(--pixel-purple)';
            imageDiv.appendChild(img);
            contentDiv.appendChild(imageDiv);

            // Meta
            const metaDiv = document.createElement('div');
            metaDiv.style.marginBottom = '1rem';
            const categorySpan = document.createElement('span');
            categorySpan.style.padding = '0.4rem 0.8rem';
            categorySpan.style.background = 'rgba(157, 78, 221, 0.3)';
            categorySpan.style.border = '1px solid var(--pixel-cyan)';
            categorySpan.style.borderRadius = '6px';
            categorySpan.style.display = 'inline-block';
            categorySpan.style.marginRight = '0.5rem';
            categorySpan.textContent = data.category;

            const creatorLink = document.createElement('a');
            creatorLink.href = `/user/${encodeURIComponent(data.creator)}`;
            creatorLink.style.color = 'var(--pixel-cyan)';
            creatorLink.className = 'creator-link';
            creatorLink.addEventListener('click', function(e) { e.stopPropagation(); });

            const creatorImg = document.createElement('img');
            creatorImg.src = data.creator_profile_pic || '/static/images/default-profile.svg';
            creatorImg.alt = `${data.creator}'s profile`;
            creatorImg.style.width = '28px';
            creatorImg.style.height = '28px';
            creatorImg.style.borderRadius = '50%';
            creatorImg.style.objectFit = 'cover';
            creatorImg.style.margin = '0 0.5rem 0 0';
            creatorImg.style.verticalAlign = 'middle';
            creatorImg.style.border = '2px solid rgba(255,255,255,0.08)';
            creatorImg.addEventListener('click', function(e) { e.stopPropagation(); });

            const nameNode = document.createElement('span');
            nameNode.textContent = data.creator;
            nameNode.className = 'creator-name';
            nameNode.style.verticalAlign = 'middle';
            creatorLink.appendChild(creatorImg);
            creatorLink.appendChild(nameNode);

            const creatorBox = document.createElement('div');
            const createdByLabel = document.createElement('span');
            createdByLabel.textContent = 'by';
            createdByLabel.style.fontFamily = "'VT323', monospace";
            createdByLabel.style.color = 'rgba(248,249,250,0.75)';
            createdByLabel.style.fontSize = '0.9rem';
            creatorBox.appendChild(createdByLabel);
            creatorBox.appendChild(creatorLink);

            metaDiv.appendChild(categorySpan);
            metaDiv.appendChild(creatorBox);
            contentDiv.appendChild(metaDiv);

            // Description
            const descDiv = document.createElement('div');
            descDiv.style.marginBottom = '1rem';
            const descHeader = document.createElement('h4');
            descHeader.style.color = 'var(--pixel-gold)';
            descHeader.style.fontFamily = "'Orbitron', sans-serif";
            descHeader.style.marginBottom = '0.5rem';
            descHeader.textContent = 'Description';
            const descText = document.createElement('p');
            descText.textContent = data.description;
            descDiv.appendChild(descHeader);
            descDiv.appendChild(descText);
            contentDiv.appendChild(descDiv);

            if (data.can_view_details) {
                const promptSection = document.createElement('div');
                promptSection.style.marginBottom = '1rem';
                promptSection.innerHTML = `
                    <h4 style="color: var(--pixel-gold); font-family: 'Orbitron', sans-serif; margin-bottom: 0.5rem;">Prompt</h4>
                    <div style="background: rgba(11, 11, 16, 0.8); padding: 1rem; border-radius: 8px; border: 2px solid var(--pixel-purple);">
                        <p id="modalPromptText" style="margin-bottom: 0;"></p>
                        <button id="copyPromptBtn" class="pixel-btn pixel-btn-secondary modal-copy-btn" style="margin-top: 1rem;">Copy Prompt</button>
                    </div>
                `;
                promptSection.querySelector('#modalPromptText').textContent = data.prompt_text;
                contentDiv.appendChild(promptSection);

                const saveBtn = document.createElement('button');
                saveBtn.id = 'toggleSaveBtn';
                saveBtn.className = 'pixel-btn' + (data.is_saved ? ' pixel-btn-primary' : '');
                saveBtn.style.marginTop = '1rem';
                saveBtn.textContent = data.is_saved ? 'Unsave' : 'Save Prompt';
                saveBtn.dataset.promptId = data.id;
                saveBtn.dataset.isSaved = data.is_saved;
                contentDiv.appendChild(saveBtn);

                saveBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const promptIdLocal = saveBtn.dataset.promptId;
                    const isSaved = saveBtn.dataset.isSaved === 'true';
                    const endpoint = isSaved ? `/unsave_prompt/${promptIdLocal}` : `/save_prompt/${promptIdLocal}`;
                    fetch(endpoint, { method: 'POST', headers: {'Content-Type': 'application/json'} })
                        .then(r => r.json())
                        .then(res => {
                            if (res.success) {
                                if (isSaved) {
                                    saveBtn.textContent = 'Save Prompt';
                                    saveBtn.classList.remove('pixel-btn-primary');
                                    saveBtn.dataset.isSaved = 'false';
                                } else {
                                    saveBtn.textContent = 'Unsave';
                                    saveBtn.classList.add('pixel-btn-primary');
                                    saveBtn.dataset.isSaved = 'true';
                                }
                            }
                        });
                });
            } else {
                contentDiv.innerHTML += `
                    <div style="background: rgba(157, 78, 221, 0.1); border: 2px solid var(--pixel-purple); border-radius: 8px; padding: 2rem; text-align: center; margin-top: 1rem;">
                        <p style="font-size: 1.2rem; margin-bottom: 1rem;">Unlock full prompt details</p>
                        ${data.can_start_trial ? 
                            '<a href="/subscription" class="pixel-btn pixel-btn-primary">Start Free Trial</a>' : 
                            '<a href="/subscription" class="pixel-btn pixel-btn-primary">Upgrade Now</a>'
                        }
                    </div>
                `;
            }

            // Edit button
            if (data.can_edit) {
                const editBtn = document.createElement('button');
                editBtn.className = 'pixel-btn pixel-btn-primary';
                editBtn.style.marginTop = '1rem';
                editBtn.style.marginLeft = '0.5rem';
                editBtn.innerHTML = '<i class="fas fa-edit"></i> Edit';
                editBtn.addEventListener('click', function() {
                    window.location.href = `/prompts/${data.slug}/edit`;
                });
                contentDiv.appendChild(editBtn);
            }

            modalContent.innerHTML = '';
            modalContent.appendChild(contentDiv);

            const copyBtn = document.getElementById('copyPromptBtn');
            if (copyBtn) {
                copyBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const text = document.getElementById('modalPromptText').textContent;
                    navigator.clipboard.writeText(text).then(() => {
                        copyBtn.textContent = 'Copied!';
                        setTimeout(() => { copyBtn.textContent = 'Copy Prompt'; }, 2000);
                    });
                });
            }

            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        })
        .catch(error => console.error('Error:', error));
}

// Close modal used in pixel gallery
function closeModal(event) {
    if (!event || event.target.id === 'promptModal') {
        const el = document.getElementById('promptModal');
        if (el) el.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// ESC key to close pixel modal
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});

// ======================
// NAVBAR DROPDOWN LOGIC
// ======================
function toggleDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    if (dropdown) dropdown.classList.toggle('show');
}

window.addEventListener('click', function(event) {
    if (!event.target.matches('.nav-dropdown-btn') && !event.target.closest('.nav-dropdown-btn')) {
        const dropdowns = document.getElementsByClassName('nav-dropdown-content');
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
});

// ======================
// PROFILE PAGE LOGIC
// ======================
document.addEventListener('DOMContentLoaded', function() {
    const profileInput = document.getElementById('profile_pic');
    const profileImage = document.getElementById('profileImage');
    if (profileInput && profileImage) {
        profileInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = function(ev) {
                    profileImage.src = ev.target.result;
                };
                reader.readAsDataURL(e.target.files[0]);
            }
        });
    }

    // Only apply username validation on profile page (guarded by presence of profileImage)
    if (profileImage) {
        const profileForm = profileImage.closest('form') || document.querySelector('form');
        if (profileForm) {
            profileForm.addEventListener('submit', function(e) {
                const usernameEl = document.getElementById('username');
                if (usernameEl) {
                    const username = usernameEl.value;
                    const pattern = /^[A-Za-z0-9_]+$/;
                    if (!pattern.test(username)) {
                        e.preventDefault();
                        Swal.fire({
                            icon: 'error',
                            title: 'Invalid Username',
                            text: 'Username can only contain letters, numbers, and underscores!',
                            confirmButtonColor: '#ff4f4f'
                        });
                    }
                }
            });
        }
    }

    if (window.innerWidth <= 768) {
        const grids = document.querySelectorAll('[style*="grid-template-columns: 1fr 1fr"]');
        grids.forEach(grid => { grid.style.gridTemplateColumns = '1fr'; });
    }
});

// ======================
// UPLOAD (ADD PROMPT) PAGE LOGIC
// ======================
document.addEventListener('DOMContentLoaded', function() {
    const urlRadio = document.getElementById('image_url_radio');
    const uploadRadio = document.getElementById('image_upload_radio');
    const urlInput = document.getElementById('url_input');
    const fileInput = document.getElementById('file_input');
    const imageUrlElement = document.getElementById('image_url');
    const imageFileElement = document.getElementById('image_file');

    function toggleImageInput() {
        if (!urlInput || !fileInput || !imageUrlElement || !imageFileElement) return;
        if (urlRadio && urlRadio.checked) {
            urlInput.style.display = 'block';
            fileInput.style.display = 'none';
            imageUrlElement.required = true;
            imageFileElement.required = false;
        } else {
            urlInput.style.display = 'none';
            fileInput.style.display = 'block';
            imageUrlElement.required = false;
            imageFileElement.required = true;
        }
    }

    if (urlRadio && uploadRadio) {
        urlRadio.addEventListener('change', toggleImageInput);
        uploadRadio.addEventListener('change', toggleImageInput);
        toggleImageInput();
    }

    const imageFile = document.getElementById('image_file');
    if (imageFile) {
        imageFile.addEventListener('change', function(e) {
            const preview = document.getElementById('image_preview');
            const file = e.target.files && e.target.files[0];
            if (!file || !preview) return;

            if (file.size > 5 * 1024 * 1024) {
                Swal.fire({
                    icon: 'error',
                    title: 'File Too Large',
                    text: 'File size must be less than 5MB',
                    confirmButtonColor: '#ff4f4f'
                });
                e.target.value = '';
                preview.innerHTML = '';
                return;
            }
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                Swal.fire({
                    icon: 'error',
                    title: 'Invalid File Type',
                    text: 'Please select a valid image file (JPEG, PNG, GIF, WebP)',
                    confirmButtonColor: '#ff4f4f'
                });
                e.target.value = '';
                preview.innerHTML = '';
                return;
            }

            const reader = new FileReader();
            reader.onload = function(ev) {
                preview.innerHTML = `
                    <div style="border: 2px solid var(--pixel-cyan); border-radius: 8px; padding: 1rem; background: rgba(0, 255, 255, 0.1);">
                        <img src="${ev.target.result}" alt="Preview" style="max-width: 100%; max-height: 300px; border-radius: 4px; display: block; margin: 0 auto;">
                        <div style="text-align: center; margin-top: 0.5rem; font-family: 'VT323', monospace; font-size: 1rem; color: rgba(248, 249, 250, 0.7);">
                            Preview: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)
                        </div>
                    </div>`;
            };
            reader.readAsDataURL(file);
        });
    }
});


