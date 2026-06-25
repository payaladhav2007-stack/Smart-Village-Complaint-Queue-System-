// GS-310: Real-Time Time-Slot Selection Availability Check
// Checks slot status before final booking confirmation
// Prevents obsolete selection states before form submittal

(function () {

  // --- Slot availability state ---
  // Mirrors the current real-time status of each slot
  // In production this would be fetched from the server API
  // Here we maintain a live state object that updates as slots fill
  var slotState = {};

  // --- Initialize slot state from existing buttons on page load ---
  function initSlotState() {
    var allButtons = document.querySelectorAll('.slot-btn');
    allButtons.forEach(function (btn) {
      var time     = btn.getAttribute('data-time');
      var capacity = btn.getAttribute('data-capacity');
      var countEl  = btn.querySelector('p:last-child');
      var countText = countEl ? countEl.textContent.trim() : '';
      var count    = 0;

      // Parse the number from text like "4 left", "2 left", "1 left"
      var match = countText.match(/(\d+)\s*left/);
      if (match) count = parseInt(match[1]);

      slotState[time] = {
        capacity: capacity, // 'available', 'limited', 'full'
        remaining: count,
        button: btn
      };
    });
  }

  // --- Simulate real-time server check for a specific slot ---
  // In production: replace this with fetch('/api/appointments/slot-status/?time=...')
  function checkSlotAvailability(time, callback) {
    // Simulate network delay (like a real server call)
    setTimeout(function () {
      var state = slotState[time];
      if (!state) {
        callback({ available: false, reason: 'Slot not found.' });
        return;
      }

      // Re-read the button's current data-capacity in case it changed
      var btn = state.button;
      var currentCapacity = btn.getAttribute('data-capacity');

      if (currentCapacity === 'full' || btn.disabled) {
        callback({
          available: false,
          status: 'full',
          reason: 'This slot just filled up. Please select another time.'
        });
      } else if (currentCapacity === 'limited') {
        callback({
          available: true,
          status: 'limited',
          reason: 'Only ' + state.remaining + ' spot(s) left for this slot. Confirm quickly!'
        });
      } else {
        callback({
          available: true,
          status: 'available',
          reason: 'Slot is available.'
        });
      }
    }, 600); // 600ms simulated server response time
  }

  // --- UI: show availability status banner ---
  function showAvailabilityBanner(message, type) {
    clearAvailabilityBanner();

    var banner = document.createElement('div');
    banner.id = 'gs-slot-banner';

    var styles = {
      base: [
        'padding: 10px 14px',
        'border-radius: 10px',
        'font-size: 0.875rem',
        'font-weight: 500',
        'margin-bottom: 12px',
        'text-align: center'
      ].join(';'),
      full: 'background: #fef2f2; border: 1px solid #fecaca; color: #dc2626;',
      limited: 'background: #fffbeb; border: 1px solid #fcd34d; color: #92400e;',
      available: 'background: #f0fdf4; border: 1px solid #bbf7d0; color: #15803d;',
      checking: 'background: #eff6ff; border: 1px solid #bfdbfe; color: #1d4ed8;'
    };

    banner.style.cssText = styles.base + styles[type];
    banner.textContent = message;

    // Insert before the selected-display div
    var selectedDisplay = document.getElementById('selected-display');
    if (selectedDisplay) {
      selectedDisplay.parentNode.insertBefore(banner, selectedDisplay);
    }
  }

  // --- UI: clear availability banner ---
  function clearAvailabilityBanner() {
    var existing = document.getElementById('gs-slot-banner');
    if (existing) existing.remove();
  }

  // --- UI: show checking spinner on confirm button ---
  function setConfirmButtonState(state) {
    var confirmBtn = document.querySelector('button[onclick="confirmSlot()"]');
    if (!confirmBtn) return;

    if (state === 'checking') {
      confirmBtn.textContent = '⏳ Checking availability...';
      confirmBtn.disabled = true;
      confirmBtn.style.opacity = '0.7';
    } else if (state === 'blocked') {
      confirmBtn.textContent = 'Slot Unavailable ✗';
      confirmBtn.disabled = true;
      confirmBtn.style.background = '#dc2626';
    } else {
      confirmBtn.textContent = 'Confirm Time Slot ✔';
      confirmBtn.disabled = false;
      confirmBtn.style.opacity = '1';
      confirmBtn.style.background = '';
    }
  }

  // --- Mark a slot as full in real time (UI update) ---
  function markSlotAsFull(time) {
    var state = slotState[time];
    if (!state) return;

    var btn = state.button;
    btn.disabled = true;
    btn.setAttribute('data-capacity', 'full');
    btn.classList.remove(
      'slot-selected', 'slot-limited',
      'border-gray-200', 'hover:border-green-400', 'hover:bg-green-50'
    );
    btn.classList.add('slot-full');
    btn.removeAttribute('onclick');

    // Update the count text to "Full 🔒"
    var countEl = btn.querySelector('p:last-child');
    if (countEl) countEl.textContent = 'Full 🔒';

    state.capacity = 'full';
    state.remaining = 0;
  }

  // --- Intercept the existing confirmSlot function ---
  // We wrap it to inject our availability check before the original logic runs
  function interceptConfirmSlot() {
    // Store reference to original confirmSlot
    var originalConfirmSlot = window.confirmSlot;

    // Override with our version
    window.confirmSlot = function () {
      var slot = document.getElementById('selected-slot').value;

      // No slot selected — let original function handle this
      if (!slot) {
        originalConfirmSlot();
        return;
      }

      // Show checking state
      setConfirmButtonState('checking');
      showAvailabilityBanner('⏳ Checking slot availability with server...', 'checking');

      // Check availability before confirming
      checkSlotAvailability(slot, function (result) {

        if (!result.available) {
          // Slot just filled up — block confirmation
          setConfirmButtonState('blocked');
          showAvailabilityBanner('🔒 ' + result.reason, 'full');

          // Update the slot button to show it's now full
          markSlotAsFull(slot);

          // Clear the selected slot
          document.getElementById('selected-slot').value = '';
          document.getElementById('selected-time').textContent = '—';
          document.getElementById('selected-display').classList.add('hidden');

          // Re-enable confirm button after 3 seconds so user can pick another
          setTimeout(function () {
            setConfirmButtonState('ready');
          }, 3000);

        } else if (result.status === 'limited') {
          // Slot is limited — warn but allow confirmation after user sees warning
          showAvailabilityBanner('⚠ ' + result.reason, 'limited');
          setConfirmButtonState('ready');

          // Auto-proceed after 2 seconds if user doesn't deselect
          setTimeout(function () {
            clearAvailabilityBanner();
            originalConfirmSlot();
          }, 2000);

        } else {
          // Slot is fully available — proceed immediately
          clearAvailabilityBanner();
          setConfirmButtonState('ready');
          originalConfirmSlot();
        }
      });
    };
  }

  // --- Also check availability when a slot button is clicked ---
  function attachSlotClickChecks() {
    var allButtons = document.querySelectorAll('.slot-btn:not([disabled])');
    allButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var time = this.getAttribute('data-time');
        if (!time) return;

        // Quick availability check on click
        checkSlotAvailability(time, function (result) {
          if (!result.available) {
            // This slot just became full while user was looking at the page
            showAvailabilityBanner(
              '🔒 ' + time + ' just filled up. Please choose another slot.',
              'full'
            );
            markSlotAsFull(time);
          } else if (result.status === 'limited') {
            showAvailabilityBanner(
              '⚠ ' + result.reason,
              'limited'
            );
          } else {
            clearAvailabilityBanner();
          }
        });
      });
    });
  }

  // --- Poll server every 30 seconds to refresh slot statuses ---
  // In production: replace fetch URL with real API endpoint
  function startPolling() {
    setInterval(function () {
      // Simulate server pushing updated slot data
      // In production this would be:
      // fetch('/api/appointments/slots/status/')
      //   .then(res => res.json())
      //   .then(data => updateAllSlots(data));

      // For now we just re-read current button states
      // to catch any changes made by other users
      var allButtons = document.querySelectorAll('.slot-btn');
      allButtons.forEach(function (btn) {
        var time = btn.getAttribute('data-time');
        if (time && slotState[time]) {
          slotState[time].capacity = btn.getAttribute('data-capacity');
        }
      });
    }, 30000); // poll every 30 seconds
  }

  // --- Main init ---
  function init() {
    initSlotState();
    interceptConfirmSlot();
    attachSlotClickChecks();
    startPolling();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();