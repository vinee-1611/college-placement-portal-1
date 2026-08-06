/* =========================================================
   College Placement Portal - Global JavaScript
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss flash messages after 5 seconds
  var alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });

  // Enable Bootstrap tooltips
  var tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  // Initialize all sidebar toggle triggers
  document.querySelectorAll("[data-toggle-sidebar]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelector(".sidebar").classList.toggle("show");
      document.querySelector(".sidebar-overlay").classList.toggle("show");
    });
  });

  // Close sidebar when clicking the overlay
  var overlay = document.querySelector(".sidebar-overlay");
  if (overlay) {
    overlay.addEventListener("click", function () {
      document.querySelector(".sidebar").classList.remove("show");
      overlay.classList.remove("show");
    });
  }
});

// Confirmation dialog for destructive actions.
// Usage: <form onsubmit="return confirmAction('Delete this item?')">
function confirmAction(message) {
  return window.confirm(message || "Are you sure you want to do this?");
}
