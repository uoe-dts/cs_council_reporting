// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize map if element exists
    if (document.getElementById('map')) {
        initMap();
    }

    // Initialize issue filters
    initIssueFilters();

    // Initialize image preview
    initImagePreview();

    // Initialize toast notifications
    initToasts();
});

// Map initialization
function initMap() {
    const map = L.map('map').setView([51.5074, -0.1278], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add markers for issues
    const issues = JSON.parse(document.getElementById('issues-data').textContent);
    issues.forEach(issue => {
        if (issue.location) {
            const marker = L.marker([issue.location.lat, issue.location.lng])
                .addTo(map)
                .bindPopup(`
                    <strong>${issue.title}</strong><br>
                    Status: ${issue.status}<br>
                    <a href="/issues/${issue.id}">View Details</a>
                `);
        }
    });
}

// Issue filters
function initIssueFilters() {
    const filterForm = document.getElementById('issue-filters');
    if (!filterForm) return;

    const filterInputs = filterForm.querySelectorAll('input, select');
    filterInputs.forEach(input => {
        input.addEventListener('change', () => {
            filterForm.submit();
        });
    });
}

// Image preview
function initImagePreview() {
    const imageInput = document.getElementById('issue-image');
    const previewContainer = document.getElementById('image-preview');
    
    if (!imageInput || !previewContainer) return;

    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewContainer.innerHTML = `
                    <img src="${e.target.result}" class="img-fluid rounded" alt="Preview">
                    <button type="button" class="btn btn-sm btn-danger mt-2" onclick="removeImage()">
                        <i class="fas fa-trash"></i> Remove
                    </button>
                `;
            };
            reader.readAsDataURL(file);
        }
    });
}

function removeImage() {
    const imageInput = document.getElementById('issue-image');
    const previewContainer = document.getElementById('image-preview');
    
    if (imageInput) imageInput.value = '';
    if (previewContainer) previewContainer.innerHTML = '';
}

// Toast notifications
function initToasts() {
    const toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    document.body.appendChild(toastContainer);
}

function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Issue status updates
function updateIssueStatus(issueId, newStatus) {
    fetch(`/api/issues/${issueId}/status/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Issue status updated successfully');
            updateStatusUI(issueId, newStatus);
        } else {
            showToast('Failed to update issue status', 'danger');
        }
    })
    .catch(error => {
        showToast('Error updating issue status', 'danger');
    });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Update UI after status change
function updateStatusUI(issueId, newStatus) {
    const statusBadge = document.querySelector(`#issue-${issueId} .status-badge`);
    if (statusBadge) {
        statusBadge.className = `status-badge status-${newStatus.toLowerCase()}`;
        statusBadge.textContent = newStatus;
    }
}

// Issue search with debounce
let searchTimeout;
function searchIssues(query) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        fetch(`/api/issues/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                updateSearchResults(data);
            })
            .catch(error => {
                showToast('Error searching issues', 'danger');
            });
    }, 300);
}

function updateSearchResults(results) {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;

    resultsContainer.innerHTML = results.map(issue => `
        <div class="issue-item">
            <h5>${issue.title}</h5>
            <p class="text-muted">${issue.description.substring(0, 100)}...</p>
            <span class="status-badge status-${issue.status.toLowerCase()}">${issue.status}</span>
            <a href="/issues/${issue.id}" class="btn btn-sm btn-primary float-end">View Details</a>
        </div>
    `).join('');
}

// Issue timeline
function initTimeline() {
    const timeline = document.querySelector('.timeline');
    if (!timeline) return;

    const items = timeline.querySelectorAll('.timeline-item');
    items.forEach((item, index) => {
        if (index % 2 === 0) {
            item.classList.add('left');
        } else {
            item.classList.add('right');
        }
    });
}

// Analytics charts
function initCharts() {
    const charts = document.querySelectorAll('.chart');
    charts.forEach(chart => {
        const ctx = chart.getContext('2d');
        const data = JSON.parse(chart.dataset.chartData);
        
        new Chart(ctx, {
            type: chart.dataset.type || 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    });
}

// Mobile menu toggle
function toggleMobileMenu() {
    const nav = document.querySelector('.navbar-nav');
    nav.classList.toggle('show');
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// File upload progress
function initFileUpload() {
    const fileInput = document.querySelector('input[type="file"]');
    if (!fileInput) return;

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const progressBar = document.createElement('div');
            progressBar.className = 'progress mt-2';
            progressBar.innerHTML = `
                <div class="progress-bar" role="progressbar" style="width: 0%"></div>
            `;
            this.parentNode.appendChild(progressBar);

            // Simulate upload progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += 10;
                progressBar.querySelector('.progress-bar').style.width = `${progress}%`;
                if (progress >= 100) {
                    clearInterval(interval);
                    setTimeout(() => progressBar.remove(), 1000);
                }
            }, 200);
        }
    });
}

// Initialize all features
document.addEventListener('DOMContentLoaded', function() {
    initTimeline();
    initCharts();
    initFileUpload();
}); 