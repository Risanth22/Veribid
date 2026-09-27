// JavaScript for AI Bid Compliance Audit System

document.addEventListener('DOMContentLoaded', function () {
  initDropzone();
  initExpandableRows();
});

function initDropzone() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const fileList = document.getElementById('selected-files-list');
  const fileCountBadge = document.getElementById('file-count-badge');
  const submitBtn = document.getElementById('btn-start-verification');

  if (!dropzone || !fileInput) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    fileInput.files = files;
    updateFileDisplay(files);
  });

  dropzone.addEventListener('click', () => {
    fileInput.click();
  });

  fileInput.addEventListener('change', (e) => {
    updateFileDisplay(e.target.files);
  });

  function updateFileDisplay(files) {
    if (!fileList) return;
    fileList.innerHTML = '';
    
    if (files.length > 0) {
      if (fileCountBadge) {
        fileCountBadge.textContent = `${files.length} file${files.length > 1 ? 's' : ''} selected`;
        fileCountBadge.classList.remove('d-none');
      }
      if (submitBtn) {
        submitBtn.disabled = false;
      }

      Array.from(files).forEach((file, idx) => {
        const pill = document.createElement('div');
        pill.className = 'file-pill';
        const sizeKb = (file.size / 1024).toFixed(1);
        pill.innerHTML = `
          <i class="fa-solid fa-file-lines text-primary"></i>
          <span class="fw-semibold">${file.name}</span>
          <span class="text-muted small">(${sizeKb} KB)</span>
        `;
        fileList.appendChild(pill);
      });
    } else {
      if (fileCountBadge) fileCountBadge.classList.add('d-none');
      if (submitBtn) submitBtn.disabled = true;
    }
  }

  // Handle form submission to show progress spinner
  const form = document.getElementById('verification-form');
  if (form) {
    form.addEventListener('submit', function() {
      const modal = new bootstrap.Modal(document.getElementById('processingModal'));
      modal.show();
    });
  }
}

function initExpandableRows() {
  const rows = document.querySelectorAll('.expandable-row');
  rows.forEach(row => {
    row.addEventListener('click', () => {
      const targetId = row.getAttribute('data-target');
      const detailsRow = document.getElementById(targetId);
      const icon = row.querySelector('.expand-icon');
      if (detailsRow) {
        if (detailsRow.classList.contains('d-none')) {
          detailsRow.classList.remove('d-none');
          if (icon) icon.className = 'fa-solid fa-chevron-up text-muted expand-icon';
        } else {
          detailsRow.classList.add('d-none');
          if (icon) icon.className = 'fa-solid fa-chevron-down text-muted expand-icon';
        }
      }
    });
  });
}
