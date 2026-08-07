// GS-REG-111: Notice Board UI

(function () {
  "use strict";

  const authToken  = document.querySelector('meta[name="auth-token"]')?.getAttribute("content");
  const userRole   = document.querySelector('meta[name="user-role"]')?.getAttribute("content");
  const userId     = parseInt(document.querySelector('meta[name="user-id"]')?.getAttribute("content"));

  let editingNoticeId = null;
  let deletingNoticeId = null;

  // ─── Load Notices on Page Load ────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {
    loadNotices();
  });

  function loadNotices() {
    fetch("/api/notices/", {
      headers: { "Authorization": `Token ${authToken}` }
    })
    .then(res => res.json())
    .then(data => renderNotices(data))
    .catch(() => {
      document.getElementById("notice-list").innerHTML =
        `<p class="text-red-400 text-center py-10">Failed to load notices. Please refresh.</p>`;
    });
  }

  // ─── Render Notice Cards ──────────────────────────────────────
  function renderNotices(notices) {
    const list = document.getElementById("notice-list");

    if (!notices || notices.length === 0) {
      list.innerHTML = `<p class="text-gray-400 text-center py-10">📭 No notices posted yet.</p>`;
      return;
    }

    // Pinned notices first
    notices.sort((a, b) => b.is_pinned - a.is_pinned);

    list.innerHTML = notices.map(notice => buildCard(notice)).join("");
  }

  function buildCard(notice) {
    const canEdit   = canEditNotice(notice);
    const pinBadge  = notice.is_pinned
      ? `<span class="bg-yellow-100 text-yellow-700 text-xs font-medium px-2 py-0.5 rounded-full">📌 Pinned</span>`
      : "";

    const actions = canEdit ? `
      <div class="flex gap-2 mt-3">
        <button onclick="openEditModal(${notice.id}, '${escapeHtml(notice.title)}', '${escapeHtml(notice.content)}', ${notice.is_pinned})"
          class="text-xs bg-blue-50 border border-blue-200 text-blue-600 px-3 py-1 rounded-lg hover:bg-blue-100">
          ✏️ Edit
        </button>
        <button onclick="openDeleteModal(${notice.id})"
          class="text-xs bg-red-50 border border-red-200 text-red-600 px-3 py-1 rounded-lg hover:bg-red-100">
          🗑️ Delete
        </button>
      </div>` : "";

    return `
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1">
            <div class="flex items-center gap-2 flex-wrap mb-1">
              <h3 class="font-semibold text-gray-800 text-base">${escapeHtml(notice.title)}</h3>
              ${pinBadge}
            </div>
            <p class="text-gray-600 text-sm leading-relaxed">${escapeHtml(notice.content)}</p>
          </div>
        </div>
        <div class="mt-3 text-xs text-gray-400">
          Posted by <span class="font-medium text-gray-500">${escapeHtml(notice.posted_by_username)}</span>
          · ${formatDate(notice.created_at)}
        </div>
        ${actions}
      </div>`;
  }

  // ─── Permission Check ─────────────────────────────────────────
  function canEditNotice(notice) {
    if (userRole === "citizen") return false;
    if (userRole === "staff") {
      // Staff can only edit their own notices, never a sarpanch's
      return notice.posted_by === userId && notice.posted_by_role !== "sarpanch";
    }
    if (userRole === "sarpanch") {
      // Sarpanch can edit their own + any staff post
      return true;
    }
    return false;
  }

  // ─── Add Modal ────────────────────────────────────────────────
  window.openAddModal = function () {
    editingNoticeId = null;
    document.getElementById("modal-title").textContent   = "Add Notice";
    document.getElementById("notice-title").value        = "";
    document.getElementById("notice-content").value      = "";
    const pin = document.getElementById("notice-pinned");
    if (pin) pin.checked = false;
    hideModalError();
    document.getElementById("notice-modal").classList.remove("hidden");
  };

  // ─── Edit Modal ───────────────────────────────────────────────
  window.openEditModal = function (id, title, content, isPinned) {
    editingNoticeId = id;
    document.getElementById("modal-title").textContent   = "Edit Notice";
    document.getElementById("notice-title").value        = title;
    document.getElementById("notice-content").value      = content;
    const pin = document.getElementById("notice-pinned");
    if (pin) pin.checked = isPinned;
    hideModalError();
    document.getElementById("notice-modal").classList.remove("hidden");
  };

  window.closeModal = function () {
    document.getElementById("notice-modal").classList.add("hidden");
  };

  // ─── Save Notice (Add or Edit) ────────────────────────────────
  window.saveNotice = function () {
    const title   = document.getElementById("notice-title").value.trim();
    const content = document.getElementById("notice-content").value.trim();
    const pinEl   = document.getElementById("notice-pinned");
    const isPinned = pinEl ? pinEl.checked : false;

    if (!title || !content) {
      showModalError("Please fill in both title and content.");
      return;
    }

    const isEdit  = editingNoticeId !== null;
    const url     = isEdit ? `/api/notices/${editingNoticeId}/` : "/api/notices/";
    const method  = isEdit ? "PATCH" : "POST";

    fetch(url, {
      method: method,
      headers: {
        "Authorization": `Token ${authToken}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ title, content, is_pinned: isPinned })
    })
    .then(res => {
      if (!res.ok) throw new Error("Save failed");
      return res.json();
    })
    .then(() => {
      closeModal();
      loadNotices();
    })
    .catch(() => showModalError("Failed to save notice. Please try again."));
  };

  // ─── Delete Modal ─────────────────────────────────────────────
  window.openDeleteModal = function (id) {
    deletingNoticeId = id;
    document.getElementById("delete-modal").classList.remove("hidden");
  };

  window.closeDeleteModal = function () {
    document.getElementById("delete-modal").classList.add("hidden");
  };

  window.confirmDelete = function () {
    if (!deletingNoticeId) return;

    fetch(`/api/notices/${deletingNoticeId}/`, {
      method: "DELETE",
      headers: { "Authorization": `Token ${authToken}` }
    })
    .then(res => {
      if (!res.ok) throw new Error("Delete failed");
      closeDeleteModal();
      loadNotices();
    })
    .catch(() => {
      closeDeleteModal();
      alert("Failed to delete notice. Please try again.");
    });
  };

  // ─── Helpers ──────────────────────────────────────────────────
  function showModalError(msg) {
    const el = document.getElementById("modal-error");
    el.textContent = msg;
    el.classList.remove("hidden");
  }

  function hideModalError() {
    document.getElementById("modal-error").classList.add("hidden");
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatDate(dateStr) {
    if (!dateStr) return "";
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
  }

})();