// GS-510: Client-Side Feedback Input Constraint Rules
// Intercepts feedback form submission, validates the star rating
// is provided (1-5) before allowing any network dispatch

(function () {

  // --- Helper: show inline error below the star rating block ---
  function showRatingError(message) {
    clearRatingError();

    var errorEl = document.createElement('p');
    errorEl.id = 'gs-rating-error';
    errorEl.style.cssText = [
      'margin-top: 10px',
      'padding: 8px 12px',
      'background: #fef2f2',
      'border: 1px solid #fecaca',
      'border-radius: 8px',
      'font-size: 0.8rem',
      'color: #dc2626',
      'font-weight: 500',
      'text-align: center'
    ].join(';');
    errorEl.textContent = '⚠ ' + message;

    var ratingLabel = document.getElementById('rating-label');
    if (ratingLabel && ratingLabel.parentNode) {
      ratingLabel.parentNode.insertBefore(errorEl, ratingLabel.nextSibling);
    }

    // Highlight the star container with a red ring
    var starContainer = document.getElementById('star-container');
    if (starContainer) {
      starContainer.style.outline = '2px solid #fecaca';
      starContainer.style.borderRadius = '12px';
      starContainer.style.padding = '6px';
    }
  }

  // --- Helper: clear inline error ---
  function clearRatingError() {
    var existing = document.getElementById('gs-rating-error');
    if (existing) existing.remove();

    var starContainer = document.getElementById('star-container');
    if (starContainer) {
      starContainer.style.outline = '';
      starContainer.style.padding = '';
    }
  }

  // --- Core: check if a valid star rating (1-5) has been selected ---
  function hasValidRating() {
    var ratingInput = document.getElementById('rating-input');
    if (!ratingInput) return true; // not on this page, skip

    var value = parseInt(ratingInput.value, 10);
    return value >= 1 && value <= 5;
  }

  // --- Watch star clicks to clear the error once a rating is picked ---
  function attachStarClearListeners() {
    var stars = document.querySelectorAll('#star-container .star-btn');
    stars.forEach(function (star) {
      star.addEventListener('click', function () {
        clearRatingError();
      });
    });
  }

  // --- Intercept form submission before any network dispatch ---
  function interceptFeedbackForm() {
    var form = document.getElementById('feedback-form');
    if (!form) return;

    // Capture phase so this runs before the existing inline
    // onclick="validateAndSubmit(event)" handler on the submit button
    form.addEventListener('submit', function (event) {
      if (!hasValidRating()) {
        event.preventDefault();
        event.stopImmediatePropagation();

        showRatingError(
          'Please select a star rating (1–5) before submitting your feedback.'
        );

        // Scroll to the rating section so the error is visible
        var starContainer = document.getElementById('star-container');
        if (starContainer) {
          starContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      } else {
        clearRatingError();
      }
    }, true); // capture phase — fires before the submit button's onclick
  }

  // --- Main init ---
  function init() {
    interceptFeedbackForm();
    attachStarClearListeners();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();