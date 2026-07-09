// GS-ADV-104: Dynamic Sub-Category JavaScript
// Binds to Mansi's 3-step form (GS-ADV-103)

document.addEventListener('DOMContentLoaded', function () {

  // ============================================================
  // LAYER 1 — MAIN CATEGORY SELECTION ENHANCEMENTS
  // ============================================================

  // Enhance selectMainCategory to also reset step 2 panels cleanly
  var originalSelectMainCategory = window.selectMainCategory;
  window.selectMainCategory = function (value, cardEl) {
    // Call Mansi's original function
    originalSelectMainCategory(value, cardEl);

    // Reset all sub-category selections when main category changes
    window._selectedSubCategory = '';
    window._selectedSubLabel = '';

    // Clear any previous subject inputs
    var personalInput = document.getElementById('personal-subject-input');
    var otherInput = document.getElementById('other-subject-input');
    if (personalInput) personalInput.value = '';
    if (otherInput) otherInput.value = '';

    // Clear subject hidden field
    var subjectHidden = document.getElementById('complaint_subject_hidden');
    if (subjectHidden) subjectHidden.value = '';

    // Deselect all category cards
    document.querySelectorAll('.category-card').forEach(function (c) {
      c.classList.remove('selected');
    });

    // Hide step2 error if visible
    var err = document.getElementById('step2-error');
    if (err) err.classList.add('hidden');
  };

  // ============================================================
  // LAYER 2 — SUB CATEGORY SELECTION ENHANCEMENTS
  // ============================================================

  var originalSelectSubCategory = window.selectSubCategory;
  window.selectSubCategory = function (value, label, cardEl) {
    // Call Mansi's original function
    originalSelectSubCategory(value, label, cardEl);

    // Store locally for validation
    window._selectedSubCategory = value;
    window._selectedSubLabel = label;

    // Government — auto-fill subject display, make it read-only
    if (window.selectedMainCategory === 'government') {
      var subjectDisplay = document.getElementById('complaint-subject-display');
      var subjectHidden = document.getElementById('complaint_subject_hidden');
      if (subjectDisplay) {
        subjectDisplay.value = label;
        subjectDisplay.readOnly = true;
        subjectDisplay.classList.add('bg-gray-50');
        subjectDisplay.classList.remove('bg-white');
      }
      if (subjectHidden) subjectHidden.value = label;
    }

    // Personal — do NOT auto-fill subject, leave manual box open
    if (window.selectedMainCategory === 'personal') {
      var personalBox = document.getElementById('personal-subject-box');
      var personalInput = document.getElementById('personal-subject-input');
      if (personalBox) personalBox.style.display = 'block';
      if (personalInput) personalInput.focus();

      // Clear subject display — citizen must type manually
      var subjectDisplay = document.getElementById('complaint-subject-display');
      if (subjectDisplay) {
        subjectDisplay.value = '';
        subjectDisplay.readOnly = false;
      }
    }
  };

  // ============================================================
  // LAYER 3 — LIVE SUBJECT SYNC FOR PERSONAL & OTHER
  // ============================================================

  // Personal subject box — sync to hidden field and display in real time
  var personalInput = document.getElementById('personal-subject-input');
  if (personalInput) {
    personalInput.addEventListener('input', function () {
      var subjectHidden = document.getElementById('complaint_subject_hidden');
      var subjectDisplay = document.getElementById('complaint-subject-display');
      if (subjectHidden) subjectHidden.value = personalInput.value.trim();
      if (subjectDisplay) subjectDisplay.value = personalInput.value.trim();

      // Clear error if user is typing
      if (personalInput.value.trim().length > 0) {
        var err = document.getElementById('step2-error');
        if (err) err.classList.add('hidden');
        personalInput.classList.remove('border-red-400');
        personalInput.classList.add('border-gray-300');
      }
    });
  }

  // Other subject box — sync to hidden field and display in real time
  var otherInput = document.getElementById('other-subject-input');
  if (otherInput) {
    otherInput.addEventListener('input', function () {
      var subjectHidden = document.getElementById('complaint_subject_hidden');
      var subjectDisplay = document.getElementById('complaint-subject-display');
      if (subjectHidden) subjectHidden.value = otherInput.value.trim();
      if (subjectDisplay) subjectDisplay.value = otherInput.value.trim();

      // Clear error if user is typing
      if (otherInput.value.trim().length > 0) {
        var err = document.getElementById('step2-error');
        if (err) err.classList.add('hidden');
        otherInput.classList.remove('border-red-400');
        otherInput.classList.add('border-gray-300');
      }
    });
  }

  // ============================================================
  // LAYER 4 — ENHANCED STEP 2 VALIDATION WITH RED HIGHLIGHTS
  // ============================================================

  var originalGoToStep3 = window.goToStep3;
  window.goToStep3 = function () {
    var mainCat = window.selectedMainCategory;

    if (mainCat === 'government') {
      if (!window.selectedSubCategory) {
        var err = document.getElementById('step2-error');
        if (err) {
          err.textContent = '⚠ Please select a sub-category to continue.';
          err.classList.remove('hidden');
        }
        // Scroll to error
        if (err) err.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
    } else if (mainCat === 'personal') {
      var personalSubject = document.getElementById('personal-subject-input');
      var hasSubCat = window.selectedSubCategory;
      var hasSubject = personalSubject && personalSubject.value.trim().length > 0;

      if (!hasSubCat || !hasSubject) {
        var err = document.getElementById('step2-error');
        if (err) {
          if (!hasSubCat && !hasSubject) {
            err.textContent = '⚠ Please select a sub-category and enter a complaint subject.';
          } else if (!hasSubCat) {
            err.textContent = '⚠ Please select a sub-category to continue.';
          } else {
            err.textContent = '⚠ Please enter a complaint subject to continue.';
          }
          err.classList.remove('hidden');
        }
        // Highlight empty subject box in red
        if (!hasSubject && personalSubject) {
          personalSubject.classList.add('border-red-400');
          personalSubject.classList.remove('border-gray-300');
          personalSubject.focus();
        }
        if (err) err.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }

    } else if (mainCat === 'other') {
      var otherSubject = document.getElementById('other-subject-input');
      if (!otherSubject || otherSubject.value.trim().length === 0) {
        var err = document.getElementById('step2-error');
        if (err) {
          err.textContent = '⚠ Please enter a complaint subject to continue.';
          err.classList.remove('hidden');
        }
        // Highlight empty box in red
        if (otherSubject) {
          otherSubject.classList.add('border-red-400');
          otherSubject.classList.remove('border-gray-300');
          otherSubject.focus();
        }
        if (err) err.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
    }

    // All valid — call Mansi's original goToStep3
    originalGoToStep3();
  };

  // ============================================================
  // LAYER 5 — ALSO UPDATE AJAX SUBMISSION TO INCLUDE NEW FIELDS
  // ============================================================

  // The existing GS-211 submit handler sends 'category' field
  // We need to also send main_category, sub_category, complaint_subject
  // We do this by intercepting FormData before it goes to the API

  var originalFormData = window.FormData;

  // Patch the form submit to inject new fields
  var complaintForm = document.getElementById('complaint-form');
  if (complaintForm) {
    complaintForm.addEventListener('submit', function () {
      // Ensure hidden fields are up to date before GS-211 handler runs
      var mainCatEl = document.getElementById('main_category');
      var subCatEl = document.getElementById('sub_category');
      var subjectEl = document.getElementById('complaint_subject_hidden');

      if (mainCatEl) mainCatEl.value = window.selectedMainCategory || '';
      if (subCatEl) subCatEl.value = window.selectedSubCategory || '';

      // Subject: Government = auto label, Personal/Other = manual input
      if (window.selectedMainCategory === 'government') {
        if (subjectEl) subjectEl.value = window.selectedSubLabel || '';
      } else if (window.selectedMainCategory === 'personal') {
        var pInput = document.getElementById('personal-subject-input');
        if (subjectEl && pInput) subjectEl.value = pInput.value.trim();
      } else if (window.selectedMainCategory === 'other') {
        var oInput = document.getElementById('other-subject-input');
        if (subjectEl && oInput) subjectEl.value = oInput.value.trim();
      }
    }, true); // capture phase — runs before GS-211 handler
  }

  console.log('GS-ADV-104: dynamic_category.js loaded successfully.');

});