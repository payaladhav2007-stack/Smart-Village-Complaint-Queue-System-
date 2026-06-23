// GS-209: Client-Side File Upload Validation
// Plugs into log_complaint.html — intercepts file input before form submits to API

(function () {

  // --- Configuration (matches Payal's GS-205 form: JPG, PNG, MP4, max 10MB) ---
  const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
  const ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo'];
  const ALLOWED_TYPES       = [...ALLOWED_IMAGE_TYPES, ...ALLOWED_VIDEO_TYPES];

  const MAX_FILE_SIZE_MB    = 10;
  const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024; // 10MB in bytes

  // --- Helper: show red error below the file input ---
  function showError(inputElement, message) {
    clearFeedback(inputElement);

    const errorEl = document.createElement('p');
    errorEl.className = 'gs-file-feedback';
    errorEl.style.cssText = [
      'color: #dc2626',
      'font-size: 0.875rem',
      'margin-top: 6px',
      'font-weight: 500',
      'padding: 8px 12px',
      'background: #fef2f2',
      'border: 1px solid #fecaca',
      'border-radius: 8px'
    ].join(';');
    errorEl.textContent = '⚠ ' + message;

    inputElement.parentNode.insertBefore(errorEl, inputElement.nextSibling);
  }

  // --- Helper: show green success below the file input ---
  function showSuccess(inputElement, fileName, sizeMB) {
    clearFeedback(inputElement);

    const successEl = document.createElement('p');
    successEl.className = 'gs-file-feedback';
    successEl.style.cssText = [
      'color: #16a34a',
      'font-size: 0.875rem',
      'margin-top: 6px',
      'font-weight: 500',
      'padding: 8px 12px',
      'background: #f0fdf4',
      'border: 1px solid #bbf7d0',
      'border-radius: 8px'
    ].join(';');
    successEl.textContent = '✓ "' + fileName + '" (' + sizeMB + ' MB) is valid and ready to upload.';

    inputElement.parentNode.insertBefore(successEl, inputElement.nextSibling);
  }

  // --- Helper: remove any existing feedback message ---
  function clearFeedback(inputElement) {
    const existing = inputElement.parentNode.querySelector('.gs-file-feedback');
    if (existing) existing.remove();
  }

  // --- Core validation logic ---
  function validateFile(inputElement) {
    const files = inputElement.files;

    // Nothing selected — clear feedback and allow
    if (!files || files.length === 0) {
      clearFeedback(inputElement);
      return true;
    }

    const file     = files[0];
    const fileType = file.type;
    const fileSize = file.size;
    const fileName = file.name;
    const sizeMB   = (fileSize / (1024 * 1024)).toFixed(2);

    // Check 1: File type must be image or video
    if (!ALLOWED_TYPES.includes(fileType)) {
      showError(
        inputElement,
        '"' + fileName + '" is not a supported file type. ' +
        'Only images (JPG, PNG, WEBP, GIF) and videos (MP4, MOV, AVI) are accepted.'
      );
      inputElement.value = ''; // clear the bad file
      return false;
    }

    // Check 2: File size must not exceed 10MB
    if (fileSize > MAX_FILE_SIZE_BYTES) {
      showError(
        inputElement,
        '"' + fileName + '" is ' + sizeMB + ' MB — exceeds the ' +
        MAX_FILE_SIZE_MB + ' MB limit. Please compress or choose a smaller file.'
      );
      inputElement.value = '';
      return false;
    }

    // All checks passed
    showSuccess(inputElement, fileName, sizeMB);
    return true;
  }

  // --- Attach listeners to all file inputs on the page ---
  function init() {
    const fileInputs = document.querySelectorAll('input[type="file"]');

    fileInputs.forEach(function (input) {
      // Validate immediately when user picks a file
      input.addEventListener('change', function () {
        validateFile(this);
      });
    });

    // Also intercept form submit — block API call if file is invalid
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
      form.addEventListener('submit', function (event) {
        let formIsValid = true;

        form.querySelectorAll('input[type="file"]').forEach(function (input) {
          if (input.files && input.files.length > 0) {
            if (!validateFile(input)) {
              formIsValid = false;
            }
          }
        });

        if (!formIsValid) {
          // Block the network/API call entirely
          event.preventDefault();
          event.stopPropagation();

          // Scroll to the error so user sees it on mobile
          const firstError = document.querySelector('.gs-file-feedback');
          if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }
      });
    });
  }

  // Run after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();