/* ============================================================
   CHECKOUT.JS — Checkout Page Interactions
   ============================================================ */

(function () {
  'use strict';

  /* ── Shipping Method Toggle ──────────────────────────────── */
  const shippingOptions = document.querySelectorAll('.shipping-option');
  const addressForm = document.getElementById('address-form');

  shippingOptions.forEach((opt) => {
    opt.addEventListener('click', function () {
      shippingOptions.forEach((o) => o.classList.remove('selected'));
      this.classList.add('selected');

      const radio = this.querySelector('input[type="radio"]');
      if (radio) radio.checked = true;

      // Show/hide address form based on shipping method
      if (addressForm) {
        addressForm.style.display = radio.value === 'pickup' ? 'none' : 'block';
      }
    });
  });

  /* ── Payment Method Toggle ──────────────────────────────── */
  const paymentOptions = document.querySelectorAll('.payment-option');

  paymentOptions.forEach((opt) => {
    opt.addEventListener('click', function () {
      paymentOptions.forEach((o) => o.classList.remove('selected'));
      this.classList.add('selected');
    });
  });

  /* ── Payment Countdown Timer ─────────────────────────────── */
  const countdownEl = document.getElementById('countdown');
  const timerBarEl = document.getElementById('timer-bar');

  if (countdownEl) {
    const totalSeconds = 24 * 60; // 24 minutes
    let remaining = totalSeconds;

    function updateTimer() {
      const mins = Math.floor(remaining / 60);
      const secs = remaining % 60;
      countdownEl.textContent =
        String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');

      if (timerBarEl) {
        timerBarEl.style.width = (remaining / totalSeconds) * 100 + '%';
      }

      if (remaining <= 0) {
        clearInterval(timerInterval);
        countdownEl.textContent = '00:00';
        countdownEl.style.color = '#dc2626';
      }

      remaining--;
    }

    updateTimer();
    const timerInterval = setInterval(updateTimer, 1000);
  }
})();
