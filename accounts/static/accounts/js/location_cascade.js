// GS-REG-106: Cascading Dropdown JavaScript

(function () {
  "use strict";

  // ─── Element References ───────────────────────────────────────
  const categoryBtns     = document.querySelectorAll(".category-btn");
  const districtSelect   = document.getElementById("district");
  const talukaSelect     = document.getElementById("taluka");
  const villageSelect    = document.getElementById("village_city");
  const documentUpload   = document.getElementById("document-upload-section");

  // ─── Category Selection (Show/Hide Document Upload) ──────────
  categoryBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const category = btn.getAttribute("data-category");

      // Highlight selected button
      categoryBtns.forEach(function (b) {
        b.classList.remove("ring-2", "ring-green-500");
      });
      btn.classList.add("ring-2", "ring-green-500");

      // Show document upload only for staff and sarpanch
      if (documentUpload) {
        if (category === "citizen") {
          documentUpload.classList.add("hidden");
        } else {
          documentUpload.classList.remove("hidden");
        }
      }

      // Store selected category
      const categoryInput = document.getElementById("selected_category");
      if (categoryInput) categoryInput.value = category;
    });
  });

  // ─── District → Fetch Talukas ─────────────────────────────────
  if (districtSelect) {
    districtSelect.addEventListener("change", function () {
      const districtId = districtSelect.value;

      // Reset downstream dropdowns
      resetDropdown(talukaSelect,  "Select Taluka");
      resetDropdown(villageSelect, "Select Village / City");

      if (!districtId) return;

      fetch(`/api/locations/talukas/?district_id=${districtId}`)
        .then(function (res) {
          if (!res.ok) throw new Error("Failed to fetch talukas");
          return res.json();
        })
        .then(function (data) {
          populateDropdown(talukaSelect, data, "Select Taluka");
        })
        .catch(function (err) {
          console.error("Taluka fetch error:", err);
          showDropdownError(talukaSelect, "Failed to load talukas");
        });
    });
  }

  // ─── Taluka → Fetch Villages ──────────────────────────────────
  if (talukaSelect) {
    talukaSelect.addEventListener("change", function () {
      const districtId = districtSelect ? districtSelect.value : "";
      const talukaId   = talukaSelect.value;

      // Reset downstream dropdown
      resetDropdown(villageSelect, "Select Village / City");

      if (!talukaId || !districtId) return;

      fetch(`/api/locations/villages/?district_id=${districtId}&taluka_id=${talukaId}`)
        .then(function (res) {
          if (!res.ok) throw new Error("Failed to fetch villages");
          return res.json();
        })
        .then(function (data) {
          populateDropdown(villageSelect, data, "Select Village / City");
        })
        .catch(function (err) {
          console.error("Village fetch error:", err);
          showDropdownError(villageSelect, "Failed to load villages");
        });
    });
  }

  // ─── Helpers ──────────────────────────────────────────────────

  function resetDropdown(selectEl, placeholder) {
    if (!selectEl) return;
    selectEl.innerHTML = `<option value="">${placeholder}</option>`;
    selectEl.disabled = true;
  }

  function populateDropdown(selectEl, data, placeholder) {
    if (!selectEl) return;
    selectEl.innerHTML = `<option value="">${placeholder}</option>`;

    if (data.length === 0) {
      selectEl.innerHTML = `<option value="">No options found</option>`;
      return;
    }

    data.forEach(function (item) {
      const option = document.createElement("option");
      option.value       = item.id;
      option.textContent = item.name;
      selectEl.appendChild(option);
    });

    selectEl.disabled = false;
  }

  function showDropdownError(selectEl, message) {
    if (!selectEl) return;
    selectEl.innerHTML = `<option value="">${message}</option>`;
    selectEl.disabled = true;
  }

})();