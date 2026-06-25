// GS-309: Client-Side JSONB Form Data Parsing & Validation
// Targets certificate_request.html — matches exact field names used by teammates

(function () {

  // Critical fields that must not be null or empty before submission
  const CRITICAL_FIELDS = [
    { name: 'service_type',       label: 'Certificate / Service Type', type: 'radio'    },
    { name: 'full_name',          label: 'Full Name',                  type: 'text'     },
    { name: 'phone_number',       label: 'Phone Number',               type: 'text'     },
    { name: 'ward_number',        label: 'Ward Number',                type: 'text'     },
    { name: 'dob',                label: 'Date of Birth',              type: 'text'     },
    { name: 'address',            label: 'Residential Address',        type: 'textarea' },
    { name: 'scheduled_time',     label: 'Time Slot',                  type: 'hidden'   },
    { name: 'declaration_truth',  label: 'Declaration (Truth)',        type: 'checkbox' },
    { name: 'declaration_terms',  label: 'Declaration (Terms)',        type: 'checkbox' }
  ];

  // --- Helper: show red error below a field ---
  function showError(fieldElement, message) {
    clearFeedback(fieldElement);

    const errorEl = document.createElement('p');
    errorEl.className = 'gs-jsonb-feedback';
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

    // For hidden/radio fields insert after parent div, else after field itself
    const insertAfter = fieldElement.closest('.service-card') ||
                        fieldElement.closest('div') ||
                        fieldElement;
    insertAfter.parentNode.insertBefore(errorEl, insertAfter.nextSibling);
  }

  // --- Helper: clear feedback for a field ---
  function clearFeedback(fieldElement) {
    const parent = fieldElement.closest('.service-card') ||
                   fieldElement.closest('div') ||
                   fieldElement.parentNode;
    const existing = parent.parentNode
      ? parent.parentNode.querySelector(
          '.gs-jsonb-feedback[data-field="' + (fieldElement.name || fieldElement.id) + '"]'
        )
      : null;
    if (existing) existing.remove();
  }

  // --- Helper: show summary error banner at top of form ---
  function showSummaryError(form, message) {
    let summary = document.getElementById('gs-jsonb-summary');
    if (!summary) {
      summary = document.createElement('div');
      summary.id = 'gs-jsonb-summary';
      summary.style.cssText = [
        'padding: 12px',
        'background: #fef2f2',
        'border: 1px solid #fecaca',
        'border-radius: 8px',
        'font-size: 0.875rem',
        'color: #dc2626',
        'font-weight: 500',
        'margin-bottom: 16px'
      ].join(';');
      form.insertBefore(summary, form.firstChild);
    }
    summary.textContent = '⚠ ' + message;
  }

  // --- Helper: clear summary error ---
  function clearSummaryError() {
    const summary = document.getElementById('gs-jsonb-summary');
    if (summary) summary.remove();
  }

  // --- Helper: get field value ---
  function getFieldValue(form, fieldName, fieldType) {
    if (fieldType === 'radio') {
      const checked = form.querySelector(
        'input[type="radio"][name="' + fieldName + '"]:checked'
      );
      return checked ? checked.value : null;
    }
    if (fieldType === 'checkbox') {
      const checkbox = form.querySelector(
        'input[type="checkbox"][name="' + fieldName + '"]'
      );
      return checkbox ? checkbox.checked : false;
    }
    const field = form.querySelector('[name="' + fieldName + '"]');
    return field ? (field.value ? field.value.trim() : null) : null;
  }

  // --- Helper: get field element ---
  function getFieldElement(form, fieldName, fieldType) {
    if (fieldType === 'radio') {
      return form.querySelector(
        'input[type="radio"][name="' + fieldName + '"]'
      );
    }
    if (fieldType === 'checkbox') {
      return form.querySelector(
        'input[type="checkbox"][name="' + fieldName + '"]'
      );
    }
    return form.querySelector('[name="' + fieldName + '"]');
  }

  // --- Core: build nested JSONB object matching Appointments table ---
  function buildJsonbObject(form) {
    return {
      applicant: {
        full_name:    getFieldValue(form, 'full_name',    'text'),
        phone_number: getFieldValue(form, 'phone_number', 'text'),
        ward_number:  getFieldValue(form, 'ward_number',  'text'),
        dob:          getFieldValue(form, 'dob',          'text'),
        address:      getFieldValue(form, 'address',      'textarea')
      },
      appointment: {
        service_type:   getFieldValue(form, 'service_type',   'radio'),
        scheduled_time: getFieldValue(form, 'scheduled_time', 'hidden'),
        purpose:        getFieldValue(form, 'purpose',        'text') || ''
      },
      declaration: {
        truth_confirmed: getFieldValue(form, 'declaration_truth', 'checkbox'),
        terms_confirmed: getFieldValue(form, 'declaration_terms', 'checkbox')
      },
      metadata: {
        submitted_at:  new Date().toISOString(),
        form_version:  '1.0'
      }
    };
  }

  // --- Core: validate all critical fields ---
  function validateForm(form) {
    let isValid = true;
    let firstErrorEl = null;

    // Remove previous feedback
    form.querySelectorAll('.gs-jsonb-feedback').forEach(function (el) {
      el.remove();
    });

    CRITICAL_FIELDS.forEach(function (field) {
      const value   = getFieldValue(form, field.name, field.type);
      const fieldEl = getFieldElement(form, field.name, field.type);
      if (!fieldEl) return; // not on this form

      let isEmpty = false;

      if (field.type === 'checkbox') {
        isEmpty = !value;
      } else if (field.type === 'radio') {
        isEmpty = !value;
      } else {
        isEmpty = !value || value === '';
      }

      if (isEmpty) {
        const errorEl = document.createElement('p');
        errorEl.className = 'gs-jsonb-feedback';
        errorEl.setAttribute('data-field', field.name);
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

        // Special messages for specific fields
        if (field.name === 'service_type') {
          errorEl.textContent = '⚠ Please select a Certificate or Service Type before submitting.';
        } else if (field.name === 'scheduled_time') {
          errorEl.textContent = '⚠ No time slot selected. Please click "Pick a Time Slot" and choose your arrival window.';
        } else if (field.name === 'declaration_truth' || field.name === 'declaration_terms') {
          errorEl.textContent = '⚠ You must accept the ' + field.label + ' declaration to proceed.';
        } else {
          errorEl.textContent = '⚠ ' + field.label + ' is required. Please fill in this field.';
        }

        // Insert error after the field's parent container
        let insertTarget;
        if (field.type === 'radio') {
          // Insert after the entire service card grid
          insertTarget = form.querySelector('.grid.grid-cols-1');
        } else if (field.type === 'checkbox') {
          insertTarget = fieldEl.closest('label');
        } else if (field.name === 'scheduled_time') {
          insertTarget = document.getElementById('slot-display');
        } else {
          insertTarget = fieldEl;
        }

        if (insertTarget && insertTarget.parentNode) {
          insertTarget.parentNode.insertBefore(errorEl, insertTarget.nextSibling);
        }

        if (!firstErrorEl) firstErrorEl = errorEl;
        isValid = false;
      }
    });

    // Extra: phone number must be 10 digits
    const phoneVal = getFieldValue(form, 'phone_number', 'text');
    const phoneEl  = getFieldElement(form, 'phone_number', 'text');
    if (phoneEl && phoneVal && !/^\d{10}$/.test(phoneVal)) {
      const phoneError = document.createElement('p');
      phoneError.className = 'gs-jsonb-feedback';
      phoneError.setAttribute('data-field', 'phone_number');
      phoneError.style.cssText = [
        'color: #dc2626',
        'font-size: 0.875rem',
        'margin-top: 6px',
        'font-weight: 500',
        'padding: 8px 12px',
        'background: #fef2f2',
        'border: 1px solid #fecaca',
        'border-radius: 8px'
      ].join(';');
      phoneError.textContent = '⚠ Phone number must be exactly 10 digits.';
      phoneEl.parentNode.insertBefore(phoneError, phoneEl.nextSibling);
      if (!firstErrorEl) firstErrorEl = phoneError;
      isValid = false;
    }

    return { isValid, firstErrorEl };
  }

  // --- Main init ---
  function init() {
    const form = document.querySelector('form');
    if (!form) return;

    form.addEventListener('submit', function (event) {

      // Step 1: Validate
      const { isValid, firstErrorEl } = validateForm(form);

      if (!isValid) {
        event.preventDefault();
        event.stopPropagation();

        showSummaryError(
          form,
          'Please complete all required fields before submitting.'
        );

        // Scroll to first error
        if (firstErrorEl) {
          firstErrorEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return;
      }

      // Step 2: Build JSONB object and inject into hidden field
      const jsonbData = buildJsonbObject(form);

      let hiddenJsonb = document.getElementById('form_data_jsonb');
      if (!hiddenJsonb) {
        hiddenJsonb = document.createElement('input');
        hiddenJsonb.type  = 'hidden';
        hiddenJsonb.name  = 'form_data_jsonb';
        hiddenJsonb.id    = 'form_data_jsonb';
        form.appendChild(hiddenJsonb);
      }
      hiddenJsonb.value = JSON.stringify(jsonbData);

      // Step 3: Clear summary and allow submission
      clearSummaryError();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();