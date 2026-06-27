// GS-410: Dynamic Live Table Search & Client-Side Filtering
// Filters grievance rows instantly by search text, category, priority and status
// Works with grievance_management.html — no page reload needed

(function () {

  // --- Core filter function ---
  function applyFilters() {
    var searchVal   = document.getElementById('gs-search').value.toLowerCase().trim();
    var categoryVal = document.getElementById('gs-category').value.toLowerCase().trim();
    var priorityVal = document.getElementById('gs-priority').value.toLowerCase().trim();
    var statusVal   = document.getElementById('gs-status').value.toLowerCase().trim();

    var rows = document.querySelectorAll('.gs-grievance-row');
    var visibleCount = 0;

    rows.forEach(function (row) {
      var rowText     = row.textContent.toLowerCase();
      var rowCategory = (row.getAttribute('data-category') || '').toLowerCase();
      var rowPriority = (row.getAttribute('data-priority') || '').toLowerCase();
      var rowStatus   = (row.getAttribute('data-status') || '').toLowerCase();

      // Check each filter
      var matchSearch   = !searchVal   || rowText.includes(searchVal);
      var matchCategory = !categoryVal || categoryVal === 'all categories' || rowCategory.includes(categoryVal);
      var matchPriority = !priorityVal || priorityVal === 'all priorities' || rowPriority.includes(priorityVal);
      var matchStatus   = !statusVal   || statusVal === 'all status'      || rowStatus.includes(statusVal);

      if (matchSearch && matchCategory && matchPriority && matchStatus) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    // Show or hide empty state message
    var emptyState = document.getElementById('gs-empty-state');
    if (emptyState) {
      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  // --- Attach event listeners ---
  function init() {
    var searchInput    = document.getElementById('gs-search');
    var categorySelect = document.getElementById('gs-category');
    var prioritySelect = document.getElementById('gs-priority');
    var statusSelect   = document.getElementById('gs-status');

    if (!searchInput) return; // not on the right page

    // Search input — filter on every keystroke
    searchInput.addEventListener('input', applyFilters);

    // Dropdowns — filter on selection change
    if (categorySelect) categorySelect.addEventListener('change', applyFilters);
    if (prioritySelect) prioritySelect.addEventListener('change', applyFilters);
    if (statusSelect)   statusSelect.addEventListener('change',   applyFilters);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();