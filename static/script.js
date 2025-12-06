// Upload page functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const photoInput = document.getElementById('photoInput');
    const selectedFiles = document.getElementById('selectedFiles');
    const fileList = document.getElementById('fileList');
    const clearBtn = document.getElementById('clearBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadForm = document.getElementById('uploadForm');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    // File selection handling
    if (photoInput) {
        photoInput.addEventListener('change', handleFileSelection);
        // Add input event for mobile compatibility
        photoInput.addEventListener('input', handleFileSelection);
        // Add additional mobile-specific events
        photoInput.addEventListener('touchend', function() {
            setTimeout(() => {
                if (photoInput.files.length > 0) {
                    handleFileSelection({ target: photoInput });
                }
            }, 100);
        });
    }

    if (uploadArea) {
        uploadArea.addEventListener('click', () => {
            console.log('Upload area clicked');
            photoInput.click();
        });
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
        
        // Add touch events for mobile
        uploadArea.addEventListener('touchstart', function(e) {
            e.preventDefault();
            console.log('Upload area touched');
        });
        
        uploadArea.addEventListener('touchend', function(e) {
            e.preventDefault();
            console.log('Upload area touch ended');
            photoInput.click();
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', clearSelection);
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
    }

    function handleFileSelection(e) {
        console.log('File selection triggered');
        const files = Array.from(e.target.files);
        console.log('Files found:', files.length);
        
        if (files.length === 0) {
            console.log('No files selected');
            return;
        }
        
        // Filter only image files
        const imageFiles = files.filter(file => {
            const isValid = file.type.startsWith('image/');
            console.log('File:', file.name, 'Type:', file.type, 'Valid:', isValid);
            return isValid;
        });
        
        console.log('Valid image files:', imageFiles.length);
        displaySelectedFiles(imageFiles);
    }

    function handleDragOver(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    }

    function handleDragLeave(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    }

    function handleDrop(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('image/'));
        
        // Create a new FileList and assign it to the input
        const dt = new DataTransfer();
        files.forEach(file => dt.items.add(file));
        photoInput.files = dt.files;
        
        displaySelectedFiles(files);
    }

    function createFileList(files) {
        const dt = new DataTransfer();
        files.forEach(file => dt.items.add(file));
        return dt.files;
    }

    function displaySelectedFiles(files) {
        if (!files || files.length === 0) {
            selectedFiles.style.display = 'none';
            clearBtn.style.display = 'none';
            uploadBtn.style.display = 'none';
            return;
        }

        fileList.innerHTML = '';
        files.forEach((file, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <strong>${file.name}</strong> 
                <span style="color: #718096;">(${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            `;
            fileList.appendChild(li);
        });

        selectedFiles.style.display = 'block';
        clearBtn.style.display = 'inline-block';
        uploadBtn.style.display = 'inline-block';
    }

    function clearSelection() {
        photoInput.value = '';
        selectedFiles.style.display = 'none';
        clearBtn.style.display = 'none';
        uploadBtn.style.display = 'none';
    }

    // Ensure file input is properly configured
    if (photoInput) {
        photoInput.multiple = true;
        photoInput.accept = 'image/*';
        
        // Add a periodic check for mobile devices
        let lastFileCount = 0;
        setInterval(() => {
            if (photoInput.files.length !== lastFileCount) {
                lastFileCount = photoInput.files.length;
                if (photoInput.files.length > 0) {
                    console.log('Files detected via periodic check');
                    handleFileSelection({ target: photoInput });
                }
            }
        }, 500);
    }

    function handleUpload(e) {
        e.preventDefault();
        
        const formData = new FormData(uploadForm);
        const files = Array.from(photoInput.files);
        
        if (files.length === 0) {
            alert('Please select at least one photo to upload.');
            return;
        }

        // Show progress
        uploadProgress.style.display = 'block';
        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Uploading...';

        // Simulate progress (since we can't track real progress with basic form submission)
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            progressFill.style.width = progress + '%';
            progressText.textContent = `Uploading... ${Math.round(progress)}%`;
        }, 200);

        // Submit form
        fetch(uploadForm.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            clearInterval(progressInterval);
            progressFill.style.width = '100%';
            progressText.textContent = 'Upload complete!';
            
            if (response.ok) {
                setTimeout(() => {
                    window.location.href = '/gallery';
                }, 1000);
            } else {
                throw new Error('Upload failed');
            }
        })
        .catch(error => {
            clearInterval(progressInterval);
            uploadProgress.style.display = 'none';
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload Photos';
            alert('Upload failed. Please try again.');
        });
    }
});

// Global variables for gallery functionality
let selectedPhotos = new Set();
let photosToDelete = [];

// Gallery page functionality
document.addEventListener('DOMContentLoaded', function() {
    const selectAllBtn = document.getElementById('selectAllBtn');
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    const photoGrid = document.getElementById('photoGrid');
    const deleteModal = document.getElementById('deleteModal');
    const cancelDelete = document.getElementById('cancelDelete');
    const confirmDelete = document.getElementById('confirmDelete');
    const deleteMessage = document.getElementById('deleteMessage');

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', toggleSelectAll);
    }

    if (deleteSelectedBtn) {
        deleteSelectedBtn.addEventListener('click', showDeleteModal);
    }

    if (cancelDelete) {
        cancelDelete.addEventListener('click', hideDeleteModal);
    }

    if (confirmDelete) {
        confirmDelete.addEventListener('click', confirmDeletePhotos);
    }

    // Close modal when clicking outside
    if (deleteModal) {
        deleteModal.addEventListener('click', function(e) {
            if (e.target === deleteModal) {
                hideDeleteModal();
            }
        });
    }

    // Add event listeners to all photo checkboxes
    const photoCheckboxes = document.querySelectorAll('.photo-check');
    photoCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const photoItem = this.closest('.photo-item');
            const filename = photoItem.dataset.filename;
            
            if (this.checked) {
                selectedPhotos.add(filename);
                photoItem.classList.add('selected');
            } else {
                selectedPhotos.delete(filename);
                photoItem.classList.remove('selected');
            }
            
            updateDeleteButton();
        });
    });

    function toggleSelectAll() {
        const checkboxes = document.querySelectorAll('.photo-check');
        const allSelected = Array.from(checkboxes).every(cb => cb.checked);
        
        checkboxes.forEach(cb => {
            cb.checked = !allSelected;
            const photoItem = cb.closest('.photo-item');
            const filename = photoItem.dataset.filename;
            
            if (cb.checked) {
                selectedPhotos.add(filename);
                photoItem.classList.add('selected');
            } else {
                selectedPhotos.delete(filename);
                photoItem.classList.remove('selected');
            }
        });

        updateDeleteButton();
        selectAllBtn.textContent = allSelected ? 'Select All' : 'Deselect All';
    }

    function updateDeleteButton() {
        if (selectedPhotos.size > 0) {
            deleteSelectedBtn.style.display = 'inline-block';
            deleteSelectedBtn.textContent = `Delete Selected (${selectedPhotos.size})`;
        } else {
            deleteSelectedBtn.style.display = 'none';
        }
    }

    function showDeleteModal() {
        photosToDelete = Array.from(selectedPhotos);
        const count = photosToDelete.length;
        deleteMessage.textContent = `Are you sure you want to delete ${count} photo${count > 1 ? 's' : ''}? This action cannot be undone.`;
        deleteModal.style.display = 'block';
    }

    function hideDeleteModal() {
        deleteModal.style.display = 'none';
        photosToDelete = [];
    }

    function confirmDeletePhotos() {
        if (photosToDelete.length === 0) return;

        // Show loading state
        confirmDelete.disabled = true;
        confirmDelete.textContent = 'Deleting...';

        // Delete photos one by one
        let deletedCount = 0;
        const totalCount = photosToDelete.length;

        photosToDelete.forEach((filename, index) => {
            fetch('/delete_photo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename: filename })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    deletedCount++;
                    // Remove photo from DOM
                    const photoItem = document.querySelector(`[data-filename="${filename}"]`);
                    if (photoItem) {
                        photoItem.remove();
                    }
                } else {
                    console.error('Failed to delete:', filename, data.message);
                }

                // Check if all deletions are complete
                if (deletedCount + (totalCount - photosToDelete.length) === totalCount) {
                    hideDeleteModal();
                    // Reload page to refresh the gallery
                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                }
            })
            .catch(error => {
                console.error('Error deleting photo:', filename, error);
                hideDeleteModal();
                alert('Some photos could not be deleted. Please try again.');
            });
        });
    }
});

// Global functions for photo interaction
function togglePhotoSelection(filename) {
    const checkbox = document.querySelector(`[data-filename="${filename}"] .photo-check`);
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        const photoItem = checkbox.closest('.photo-item');
        
        if (checkbox.checked) {
            selectedPhotos.add(filename);
            photoItem.classList.add('selected');
        } else {
            selectedPhotos.delete(filename);
            photoItem.classList.remove('selected');
        }
        
        updateDeleteButton();
    }
}

function deletePhoto(filename) {
    if (confirm(`Are you sure you want to delete this photo?`)) {
        fetch('/delete_photo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: filename })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove photo from DOM
                const photoItem = document.querySelector(`[data-filename="${filename}"]`);
                if (photoItem) {
                    photoItem.remove();
                }
            } else {
                alert('Failed to delete photo: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error deleting photo:', error);
            alert('Error deleting photo. Please try again.');
        });
    }
}
