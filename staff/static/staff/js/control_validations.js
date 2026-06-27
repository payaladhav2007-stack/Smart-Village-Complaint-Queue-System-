// GS-409: Client-Side Reassignment and Control Validations
(function () {

  function showErrorToast(message) {
    var toast = document.getElementById('toast');
    var toastIcon = document.getElementById('toast-icon');
    var toastMsg  = document.getElementById('toast-message');
    if (!toast || !toastIcon || !toastMsg) return;
    var innerDiv = toast.querySelector('div');
    if (innerDiv) {
      innerDiv.style.background = '#fef2f2';
      innerDiv.style.color      = '#dc2626';
      innerDiv.style.border     = '1px solid #fecaca';
    }
    toastIcon.textContent = 'Warning';
    toastMsg.textContent  = message;
    toast.classList.remove('hidden');
    clearTimeout(toast._hideTimer);
    toast._hideTimer = setTimeout(function () {
      toast.classList.add('hidden');
      if (innerDiv) {
        innerDiv.style.background = '#1f2937';
        innerDiv.style.color      = '#f9fafb';
        innerDiv.style.border     = 'none';
      }
    }, 3500);
  }

  function showInlineError(targetEl, message, errorId) {
    var old = document.getElementById(errorId);
    if (old) old.remove();
    var errorEl = document.createElement('div');
    errorEl.id = errorId;
    errorEl.style.cssText = [
      'margin-top:8px',
      'padding:8px 12px',
      'background:#fef2f2',
      'border:1px solid #fecaca',
      'border-radius:8px',
      'font-size:0.8rem',
      'color:#dc2626',
      'font-weight:500'
    ].join(';');
    errorEl.textContent = 'Warning: ' + message;
    if (targetEl && targetEl.parentNode) {
      targetEl.parentNode.insertBefore(errorEl, targetEl.nextSibling);
    }
    setTimeout(function () {
      var el = document.getElementById(errorId);
      if (el) el.remove();
    }, 4000);
  }

  function validateAppointmentCard(card) {
    var counterBtn = card.querySelector('[onclick^="toggleDropdown(\'dd"]');
    if (!counterBtn) return true;
    var counterLabel = counterBtn.textContent.replace('\u25be', '').trim();
    if (!counterLabel || counterLabel === '' || counterLabel === 'Unassigned') {
      showInlineError(
        counterBtn,
        'Please select a Counter Number before updating this appointment status.',
        'error-appt-' + Date.now()
      );
      showErrorToast('Select a Counter Number before updating status.');
      return false;
    }
    return true;
  }

  function validateGrievanceCard(card) {
    var workerBtn = card.querySelector('[onclick^="toggleDropdown(\'gdd"]');
    if (!workerBtn) return true;
    var workerLabel = workerBtn.textContent.replace('\u25be', '').trim();
    if (!workerLabel || workerLabel === '' || workerLabel === 'Unassigned') {
      showInlineError(
        workerBtn,
        'Please assign a Field Worker before updating this grievance status.',
        'error-grv-' + Date.now()
      );
      showErrorToast('Assign a Field Worker before updating grievance status.');
      return false;
    }
    return true;
  }

  function interceptStatusButtons() {
    document.querySelectorAll('[onclick^="setStatus"]').forEach(function (btn) {
      btn.addEventListener('click', function (event) {
        var card = btn.closest('.bg-white');
        if (!card) return;
        var isValid = validateAppointmentCard(card);
        if (!isValid) {
          event.stopImmediatePropagation();
          var orig = window.setStatus;
          window.setStatus = function () { window.setStatus = orig; };
          setTimeout(function () { window.setStatus = orig; }, 100);
        }
      }, true);
    });

    document.querySelectorAll('[onclick^="setGrievanceStatus"]').forEach(function (btn) {
      btn.addEventListener('click', function (event) {
        var card = btn.closest('.bg-white');
        if (!card) return;
        if (card.classList.contains('opacity-70')) return;
        var isValid = validateGrievanceCard(card);
        if (!isValid) {
          event.stopImmediatePropagation();
          var orig = window.setGrievanceStatus;
          window.setGrievanceStatus = function () { window.setGrievanceStatus = orig; };
          setTimeout(function () { window.setGrievanceStatus = orig; }, 100);
        }
      }, true);
    });
  }

  function trackReassignments() {
    var originalReassign = window.reassign;
    if (originalReassign) {
      window.reassign = function (dropdownId, value) {
        var dropdown = document.getElementById(dropdownId);
        if (dropdown) {
          var card = dropdown.closest('.bg-white');
          if (card) {
            card.querySelectorAll('[id^="error-"]').forEach(function (el) {
              el.remove();
            });
          }
        }
        originalReassign(dropdownId, value);
      };
    }
  }

  function init() {
    interceptStatusButtons();
    trackReassignments();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();