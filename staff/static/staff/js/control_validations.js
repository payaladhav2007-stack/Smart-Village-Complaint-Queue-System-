// GS-409: Client-Side Reassignment and Control Validations
// Protects staff console actions in control_panel.html before any API dispatch
// Validates counter reassignment, field worker assignment, and status transitions

(function () {

  // --- Tracking state: which cards have valid assignments ---
  var appointmentAssignments = {};  // cardId -> counter value
  var grievanceAssignments    = {};  // cardId -> field worker value

  // --- Helper: show inline red error below a target element ---
  function showInlineError(targetEl, message, errorId) {
    // Remove existing error for this target
    clearInlineError(errorId);

    var errorEl = document.createElement('div');
    errorEl.id  = errorId;
    errorEl.style.cssText = [
      'margin-top: 8px',
      'padding: 8px 12px',
      'background: #fef2f2',
      'border: 1px solid #fecaca',
      'border-radius: 8px',
      'font-size: 0.8rem',
      'color: #dc2626',
      'font-weight: 500'
    ].join(';');
    errorEl.textContent = '⚠ ' + message;

    targetEl.parentNode.insertBefore(errorEl, targetEl.nextSibling);

    // Auto-remove after 4 seconds
    setTimeout(function () { clearInlineError(errorId); }, 4000);
  }

  // --- Helper: clear inline error by id ---
  function clearInlineError(errorId) {
    var existing = document.getElementById(errorId);
    if (existing) existing.remove();
  }

  // --- Helper: show toast notification (reuses existing toast if present) ---
  function showValidationToast(icon, message, isError) {
    var toast = document.getElementById('gs-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'gs-toast';
      toast.style.cssText = [
        'position: fixed',
        'bottom: 24px',
        'right: 24px',
        'z-index: 9999',
        'padding: 12px 18px',
        'border-radius: 10px',
        'font-size: 0.875rem',
        'font-weight: 500',
        'display: flex',
        'align-items: center',
        'gap: 8px',
        'box-shadow: 0 4px 12px rgba(0,0,0,0.15)',
        'transition: opacity 0.3s ease'
      ].join(';');
      document.body.appendChild(toast);
    }

    toast.style.background = isError ? '#fef2f2'  : '#1f2937';
    toast.style.color      = isError ? '#dc2626'  : '#f9fafb';
    toast.style.border     = isError ? '1px solid #fecaca' : 'none';
    toast.textContent      = icon + ' ' + message;
    toast.style.opacity    = '1';

    clearTimeout(toast._hideTimer);
    toast._hideTimer = setTimeout(function () {
      toast.style.opacity = '0';
    }, 3000);
  }

  // --- Validate counter reassignment for appointments ---
  function validateCounterReassignment(cardEl, cardId) {
    var assignment = appointmentAssignments[cardId];

    if (!assignment || assignment === '') {
      showInlineError(
        cardEl.querySelector('.gs-counter-btn') || cardEl,
        'Please select a Counter Number before changing this appointment\'s status.',
        'error-counter-' + cardId
      );
      showValidationToast('⚠', 'Select a counter before updating status.', true);
      return false;
    }

    clearInlineError('error-counter-' + cardId);
    return true;
  }

  // --- Validate field worker assignment for grievances ---
  function validateWorkerAssignment(cardEl, cardId) {
    var assignment = grievanceAssignments[cardId];

    if (!assignment || assignment === '') {
      showInlineError(
        cardEl.querySelector('.gs-worker-btn') || cardEl,
        'Please assign a Field Worker before updating this grievance\'s status.',
        'error-worker-' + cardId
      );
      showValidationToast('⚠', 'Assign a field worker before updating status.', true);
      return false;
    }

    clearInlineError('error-worker-' + cardId);
    return true;
  }

  // --- Validate status transition logic ---
  function validateStatusTransition(currentStatus, newStatus, type) {
    // Legal transitions matching GS-403 state machine
    var legalTransitions = {
      grievance: {
        'pending':     ['in_progress', 'rejected'],
        'in_progress': ['resolved', 'rejected'],
        'resolved':    [],
        'rejected':    []
      },
      appointment: {
        'pending':     ['confirmed', 'cancelled'],
        'confirmed':   ['completed', 'cancelled'],
        'completed':   [],
        'cancelled':   []
      }
    };

    var allowed = legalTransitions[type] && legalTransitions[type][currentStatus];
    if (!allowed) return true; // unknown state, allow and let backend handle

    if (allowed.length === 0) {
      showValidationToast(
        '🔒',
        'This ticket is locked (' + currentStatus + ') and cannot be updated further.',
        true
      );
      return false;
    }

    if (allowed.indexOf(newStatus) === -1) {
      showValidationToast(
        '⚠',
        'Cannot move from "' + currentStatus + '" to "' + newStatus + '". Invalid transition.',
        true
      );
      return false;
    }

    return true;
  }

  // --- Intercept appointment status buttons ---
  function interceptAppointmentButtons() {
    var appointmentCards = document.querySelectorAll('[data-card-type="appointment"]');

    appointmentCards.forEach(function (card) {
      var cardId = card.getAttribute('data-card-id');
      if (!cardId) return;

      // Initialize assignment tracking
      appointmentAssignments[cardId] = card.getAttribute('data-counter') || '';

      var statusBtns = card.querySelectorAll('[data-status-action]');
      statusBtns.forEach(function (btn) {
        btn.addEventListener('click', function (event) {
          var newStatus     = btn.getAttribute('data-status-action');
          var currentStatus = card.getAttribute('data-current-status') || 'pending';

          // Check 1: Counter must be assigned
          var counterValid = validateCounterReassignment(card, cardId);
          if (!counterValid) {
            event.stopImmediatePropagation();
            return;
          }

          // Check 2: Transition must be legal
          var transitionValid = validateStatusTransition(currentStatus, newStatus, 'appointment');
          if (!transitionValid) {
            event.stopImmediatePropagation();
            return;
          }

          // All valid — update current status tracking
          card.setAttribute('data-current-status', newStatus);
          showValidationToast('✔', 'Appointment status updated to: ' + newStatus, false);
        });
      });

      // Track counter reassignment selections
      var counterDropdownItems = card.querySelectorAll('[data-counter-value]');
      counterDropdownItems.forEach(function (item) {
        item.addEventListener('click', function () {
          var counterVal = item.getAttribute('data-counter-value');
          appointmentAssignments[cardId] = counterVal;
          card.setAttribute('data-counter', counterVal);
          clearInlineError('error-counter-' + cardId);
        });
      });
    });
  }

  // --- Intercept grievance status buttons ---
  function interceptGrievanceButtons() {
    var grievanceCards = document.querySelectorAll('[data-card-type="grievance"]');

    grievanceCards.forEach(function (card) {
      var cardId = card.getAttribute('data-card-id');
      if (!cardId) return;

      // Initialize assignment tracking
      grievanceAssignments[cardId] = card.getAttribute('data-worker') || '';

      var statusBtns = card.querySelectorAll('[data-grievance-action]');
      statusBtns.forEach(function (btn) {
        btn.addEventListener('click', function (event) {
          var newStatus     = btn.getAttribute('data-grievance-action');
          var currentStatus = card.getAttribute('data-current-status') || 'pending';

          // Check 1: Field worker must be assigned
          // Resolved cards skip this check
          if (currentStatus !== 'resolved') {
            var workerValid = validateWorkerAssignment(card, cardId);
            if (!workerValid) {
              event.stopImmediatePropagation();
              return;
            }
          }

          // Check 2: Transition must be legal
          var transitionValid = validateStatusTransition(currentStatus, newStatus, 'grievance');
          if (!transitionValid) {
            event.stopImmediatePropagation();
            return;
          }

          // All valid — update current status tracking
          card.setAttribute('data-current-status', newStatus);
          showValidationToast('✔', 'Grievance status updated to: ' + newStatus, false);
        });
      });

      // Track field worker assignment selections
      var workerDropdownItems = card.querySelectorAll('[data-worker-value]');
      workerDropdownItems.forEach(function (item) {
        item.addEventListener('click', function () {
          var workerVal = item.getAttribute('data-worker-value');
          grievanceAssignments[cardId] = workerVal;
          card.setAttribute('data-worker', workerVal);
          clearInlineError('error-worker-' + cardId);
        });
      });
    });
  }

  // --- Intercept any forms inside the staff console ---
  function interceptConsoleForms() {
    var forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
      form.addEventListener('submit', function (event) {
        var hasError = false;

        // Check all required selects inside the form
        var selects = form.querySelectorAll('select[required]');
        selects.forEach(function (sel) {
          if (!sel.value || sel.value === '') {
            showInlineError(
              sel,
              'This field is required before submitting.',
              'error-select-' + (sel.name || sel.id || Math.random())
            );
            hasError = true;
          }
        });

        // Check all required inputs inside the form
        var inputs = form.querySelectorAll('input[required]');
        inputs.forEach(function (inp) {
          if (!inp.value || inp.value.trim() === '') {
            showInlineError(
              inp,
              'This field is required before submitting.',
              'error-input-' + (inp.name || inp.id || Math.random())
            );
            hasError = true;
          }
        });

        if (hasError) {
          event.preventDefault();
          event.stopPropagation();
          showValidationToast('⚠', 'Please complete all required fields before submitting.', true);
        }
      });
    });
  }

  // --- Main init ---
  function init() {
    interceptAppointmentButtons();
    interceptGrievanceButtons();
    interceptConsoleForms();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();