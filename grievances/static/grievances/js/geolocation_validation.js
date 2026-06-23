// GS-210: Client-Side Geolocation Validation Logic
// Ensures latitude and longitude are set before grievance form submits

(function () {

  // --- Helper: show red error message below a target element ---
  function showError(targetElement, message) {
    clearFeedback(targetElement);

    const errorEl = document.createElement('p');
    errorEl.className = 'gs-geo-feedback';
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

    targetElement.parentNode.insertBefore(errorEl, targetElement.nextSibling);
  }

  // --- Helper: clear existing feedback ---
  function clearFeedback(targetElement) {
    const existing = targetElement.parentNode.querySelector('.gs-geo-feedback');
    if (existing) existing.remove();
  }

  // --- Helper: show fallback prompt if geolocation is denied ---
  function showGeolocationDeniedPrompt(targetElement) {
    clearFeedback(targetElement);

    const promptEl = document.createElement('div');
    promptEl.className = 'gs-geo-feedback';
    promptEl.style.cssText = [
      'margin-top: 8px',
      'padding: 12px',
      'background: #fffbeb',
      'border: 1px solid #fcd34d',
      'border-radius: 8px',
      'font-size: 0.875rem',
      'color: #92400e'
    ].join(';');
    promptEl.innerHTML = [
      '<strong>⚠ Location access was denied.</strong><br>',
      'Your browser blocked location access. To submit this complaint, ',
      'please use the <strong>📍 Pick Location on Map</strong> button above ',
      'to manually select your location on the map instead.'
    ].join('');

    targetElement.parentNode.insertBefore(promptEl, targetElement.nextSibling);
  }

  // --- Core: validate latitude and longitude fields ---
  function validateCoordinates() {
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    const locationDisplay = document.getElementById('location-display');

    // If hidden fields don't exist on this page, skip validation
    if (!latInput || !lngInput) return true;

    const lat = latInput.value.trim();
    const lng = lngInput.value.trim();

    // Check 1: Fields must not be empty
    if (!lat || !lng) {
      showError(
        locationDisplay,
        'Location is required. Please click "📍 Pick Location on Map" and drop a pin on your location before submitting.'
      );
      return false;
    }

    // Check 2: Values must not be zero (default unset state)
    const latNum = parseFloat(lat);
    const lngNum = parseFloat(lng);

    if (latNum === 0 && lngNum === 0) {
      showError(
        locationDisplay,
        'Invalid location detected (0, 0). Please re-pick your location on the map.'
      );
      return false;
    }

    // Check 3: Latitude must be between -90 and 90
    if (latNum < -90 || latNum > 90) {
      showError(
        locationDisplay,
        'Invalid latitude value. Please re-pick your location on the map.'
      );
      return false;
    }

    // Check 4: Longitude must be between -180 and 180
    if (lngNum < -180 || lngNum > 180) {
      showError(
        locationDisplay,
        'Invalid longitude value. Please re-pick your location on the map.'
      );
      return false;
    }

    // All checks passed — clear any existing error
    clearFeedback(locationDisplay);
    return true;
  }

  // --- Geolocation denial handler ---
  function handleGeolocationDenied() {
    const locationDisplay = document.getElementById('location-display');
    if (locationDisplay) {
      showGeolocationDeniedPrompt(locationDisplay);
    }
  }

  // --- Watch for browser geolocation permission denial ---
  function watchGeolocationPermission() {
    if (!navigator.geolocation) return;

    // Only fires if the browser supports the Permissions API
    if (navigator.permissions) {
      navigator.permissions.query({ name: 'geolocation' }).then(function (result) {
        if (result.state === 'denied') {
          handleGeolocationDenied();
        }
        // Watch for permission state changes in real time
        result.onchange = function () {
          if (this.state === 'denied') {
            handleGeolocationDenied();
          } else {
            const locationDisplay = document.getElementById('location-display');
            if (locationDisplay) clearFeedback(locationDisplay);
          }
        };
      });
    }
  }

  // --- Attach form submit interception ---
  function init() {
    // Watch geolocation permission immediately on page load
    watchGeolocationPermission();

    // Intercept form submission
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
      form.addEventListener('submit', function (event) {
        const coordsValid = validateCoordinates();

        if (!coordsValid) {
          // Block form submission and API call entirely
          event.preventDefault();
          event.stopPropagation();

          // Scroll to the error so it's visible on mobile
          const error = document.querySelector('.gs-geo-feedback');
          if (error) {
            error.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }
      });
    });

    // Also validate in real time when location-display div changes
    // (triggered after receiveLocation() is called from map popup)
    const latInput = document.getElementById('latitude');
    if (latInput) {
      latInput.addEventListener('change', function () {
        validateCoordinates();
      });
    }
  }

  // Run after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();