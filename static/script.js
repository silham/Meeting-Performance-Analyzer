// API base URL
const API_URL = window.location.origin;

// Current job ID for tracking
let currentJobId = null;
let pollInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadJobs();
    
    // Auto-refresh jobs every 5 seconds
    setInterval(loadJobs, 5000);
});

function setupEventListeners() {
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    
    // File input change
    fileInput.addEventListener('change', function(e) {
        const fileName = e.target.files[0]?.name || 'Choose video or audio file';
        document.getElementById('fileName').textContent = fileName;
    });
    
    // Form submit
    uploadForm.addEventListener('submit', handleSubmit);
}

async function handleSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = document.getElementById('submitBtn');
    const progressContainer = document.getElementById('uploadProgress');
    const progressText = document.getElementById('progressText');
    const progressFill = document.getElementById('progressFill');
    
    // Disable submit button
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="btn-icon">⏳</span> Uploading...';
    
    // Show progress
    progressContainer.style.display = 'block';
    progressFill.style.width = '50%';
    progressText.textContent = 'Uploading file...';
    
    try {
        const response = await fetch(`${API_URL}/api/transcribe`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        const result = await response.json();
        currentJobId = result.job_id;
        
        // Update progress
        progressFill.style.width = '100%';
        progressText.textContent = 'Upload complete! Processing...';
        
        // Reset form
        form.reset();
        document.getElementById('fileName').textContent = 'Choose video or audio file';
        
        // Show success message
        showNotification('File uploaded successfully! Transcription in progress...', 'success');
        
        // Reload jobs list
        await loadJobs();
        
        // Scroll to jobs list
        document.getElementById('jobsList').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Upload error:', error);
        showNotification(error.message || 'Failed to upload file', 'error');
        progressFill.style.width = '0%';
    } finally {
        // Re-enable submit button
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span class="btn-icon">🚀</span> Start Transcription';
            progressContainer.style.display = 'none';
            progressFill.style.width = '0%';
        }, 2000);
    }
}

async function loadJobs() {
    try {
        const response = await fetch(`${API_URL}/api/jobs?limit=20`);
        if (!response.ok) throw new Error('Failed to load jobs');
        
        const data = await response.json();
        displayJobs(data.jobs);
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

function displayJobs(jobs) {
    const jobsList = document.getElementById('jobsList');
    
    if (!jobs || jobs.length === 0) {
        jobsList.innerHTML = '<p class="text-muted">No jobs yet. Upload a file to get started!</p>';
        return;
    }
    
    jobsList.innerHTML = jobs.map(job => createJobCard(job)).join('');
}

function createJobCard(job) {
    const statusClass = `status-${job.status}`;
    const statusIcon = {
        'queued': '⏳',
        'processing': '⚙️',
        'completed': '✅',
        'failed': '❌'
    }[job.status] || '📄';
    
    const createdDate = new Date(job.created_at).toLocaleString();
    
    let actionsHtml = '';
    if (job.status === 'completed') {
        actionsHtml = `
            <button class="btn btn-primary" onclick="viewTranscription('${job.job_id}')">
                <span class="btn-icon">👁️</span>
                View
            </button>
            <button class="btn btn-success" onclick="downloadTranscription('${job.job_id}')">
                <span class="btn-icon">💾</span>
                Download
            </button>
        `;
    } else if (job.status === 'failed') {
        actionsHtml = `
            <button class="btn btn-danger" onclick="deleteJob('${job.job_id}')">
                <span class="btn-icon">🗑️</span>
                Delete
            </button>
        `;
    }
    
    return `
        <div class="job-item">
            <div class="job-header">
                <div class="job-title">${job.filename}</div>
                <div class="job-status ${statusClass}">
                    ${statusIcon} ${job.status.toUpperCase()}
                </div>
            </div>
            <div class="job-info">
                📅 ${createdDate} • 🆔 ${job.job_id.substring(0, 8)}...
            </div>
            ${job.progress ? `<div class="job-progress">${job.progress}</div>` : ''}
            ${job.error ? `<div class="job-progress" style="color: var(--danger-color);">Error: ${job.error}</div>` : ''}
            ${actionsHtml ? `<div class="job-actions">${actionsHtml}</div>` : ''}
        </div>
    `;
}

async function viewTranscription(jobId) {
    try {
        const response = await fetch(`${API_URL}/api/jobs/${jobId}`);
        if (!response.ok) throw new Error('Failed to load transcription');
        
        const job = await response.json();
        
        if (!job.transcription) {
            showNotification('Transcription not available', 'error');
            return;
        }
        
        // Show modal
        const modal = document.getElementById('resultModal');
        const content = document.getElementById('transcriptionContent');
        const downloadBtn = document.getElementById('downloadBtn');
        
        content.textContent = job.transcription;
        downloadBtn.onclick = () => downloadTranscription(jobId);
        
        modal.style.display = 'flex';
        
    } catch (error) {
        console.error('Error viewing transcription:', error);
        showNotification('Failed to load transcription', 'error');
    }
}

async function downloadTranscription(jobId) {
    try {
        const response = await fetch(`${API_URL}/api/jobs/${jobId}/download`);
        if (!response.ok) throw new Error('Failed to download');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transcription_${jobId}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('Download started!', 'success');
    } catch (error) {
        console.error('Download error:', error);
        showNotification('Failed to download transcription', 'error');
    }
}

async function deleteJob(jobId) {
    if (!confirm('Are you sure you want to delete this job?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/jobs/${jobId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete job');
        
        showNotification('Job deleted successfully', 'success');
        await loadJobs();
    } catch (error) {
        console.error('Delete error:', error);
        showNotification('Failed to delete job', 'error');
    }
}

function closeModal() {
    document.getElementById('resultModal').style.display = 'none';
}

function copyTranscription() {
    const content = document.getElementById('transcriptionContent').textContent;
    
    navigator.clipboard.writeText(content).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showNotification('Failed to copy', 'error');
    });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? 'var(--success-color)' : type === 'error' ? 'var(--danger-color)' : 'var(--primary-color)'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    const modal = document.getElementById('resultModal');
    if (e.target === modal) {
        closeModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});
