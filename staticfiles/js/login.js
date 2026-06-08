/* ============================================================
   login.js — Kahta Grafika Login Page
   Place in: static/js/login.js
   ============================================================ */

(function () {
  'use strict';

  /* ── Password toggle ── */
  function initPasswordToggle() {
    const toggle   = document.getElementById('togglePassword');
    const input    = document.getElementById('id_password');
    const eyeOpen  = toggle?.querySelector('.eye-open');
    const eyeClosed = toggle?.querySelector('.eye-closed');

    if (!toggle || !input) return;

    toggle.addEventListener('click', function () {
      const isPassword = input.type === 'password';

      input.type = isPassword ? 'text' : 'password';
      eyeOpen.style.display  = isPassword ? 'none'  : '';
      eyeClosed.style.display = isPassword ? '' : 'none';

      toggle.setAttribute('aria-label', isPassword ? 'Sembunyikan password' : 'Tampilkan password');
    });
  }

  /* ── Form submit with loading state ── */
  function initFormLoading() {
    const form = document.getElementById('loginForm');
    const btn  = document.getElementById('submitBtn');

    if (!form || !btn) return;

    form.addEventListener('submit', function () {
      // Basic HTML5 validation before loading state
      if (!form.checkValidity()) return;

      btn.classList.add('is-loading');
      btn.disabled = true;

      // Safety: re-enable after 10 s (in case of server error / redirect timeout)
      setTimeout(function () {
        btn.classList.remove('is-loading');
        btn.disabled = false;
      }, 10_000);
    });
  }

  /* ── Input focus: float label effect ── */
  function initInputFocus() {
    const inputs = document.querySelectorAll('.field-input');

    inputs.forEach(function (input) {
      // Mark pre-filled inputs on page load
      if (input.value.trim()) {
        input.closest('.field-group')?.classList.add('has-value');
      }

      input.addEventListener('input', function () {
        const group = input.closest('.field-group');
        if (!group) return;
        group.classList.toggle('has-value', input.value.trim().length > 0);
      });
    });
  }

  /* ── Auto-dismiss flash messages (if any) ── */
  function initAlertAutoDismiss() {
    const alert = document.querySelector('.alert-error');
    if (!alert) return;

    setTimeout(function () {
      alert.style.transition = 'opacity 0.4s ease, max-height 0.4s ease, margin 0.4s ease';
      alert.style.opacity = '0';
      alert.style.maxHeight = '0';
      alert.style.margin = '0';
      alert.style.overflow = 'hidden';
    }, 5000);
  }

  /* ── Init all ── */
  document.addEventListener('DOMContentLoaded', function () {
    initPasswordToggle();
    initFormLoading();
    initInputFocus();
    initAlertAutoDismiss();
  });

})();