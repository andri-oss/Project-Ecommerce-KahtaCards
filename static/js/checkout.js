/* ============================================================
   CHECKOUT.JS — Checkout Page Interactions
   Kahta Grafika | Vanilla JS, no dependencies
   ============================================================ */

(function () {
  'use strict';

  /* ── Helper: format number as IDR string ───────────────── */
  function formatIDR(num) {
    return 'Rp ' + Math.round(num).toLocaleString('id-ID');
  }

  /* ── Shipping Method Toggle ──────────────────────────────── */
  const shippingOptions  = document.querySelectorAll('.shipping-option');
  const addressForm      = document.getElementById('address-form');
  const pickupInfoCard   = document.getElementById('pickup-info');
  const shippingDisplay  = document.getElementById('shipping-fee-display');
  const totalDisplay     = document.getElementById('total-display');

  // Address fields that are conditionally required
  const addressFields = addressForm
    ? addressForm.querySelectorAll('input, select, textarea')
    : [];

  const SHIPPING_FEE = 25000;  // flat rate delivery
  const TAX_RATE     = 0.11;

  function updateSummary(isDelivery) {
    if (!shippingDisplay || !totalDisplay || typeof window.CART_SUBTOTAL === 'undefined') return;
    const subtotal    = parseFloat(window.CART_SUBTOTAL) || 0;
    const shippingFee = isDelivery ? SHIPPING_FEE : 0;
    const tax         = Math.round(subtotal * TAX_RATE);
    const total       = subtotal + shippingFee + tax;

    if (isDelivery) {
      shippingDisplay.textContent = formatIDR(SHIPPING_FEE);
      shippingDisplay.style.color = 'var(--color-text)';
    } else {
      shippingDisplay.innerHTML = '<span class="badge-free">GRATIS</span>';
    }
    totalDisplay.textContent = formatIDR(total);
    totalDisplay.style.color = 'var(--color-accent)';
  }

  function setAddressRequired(required) {
    addressFields.forEach(function (field) {
      // only toggle required on fields that actually need it for delivery
      const name = field.name || '';
      if (['province', 'city', 'postal_code', 'address'].includes(name)) {
        if (required) {
          field.setAttribute('required', '');
        } else {
          field.removeAttribute('required');
        }
      }
    });
  }

  function applyShippingMethod(value) {
    const isDelivery = value !== 'pickup';

    // Address form visibility with smooth animation
    if (addressForm) {
      if (isDelivery) {
        addressForm.style.display = 'block';
        requestAnimationFrame(function () {
          addressForm.classList.add('form-visible');
          addressForm.classList.remove('form-hidden');
        });
      } else {
        addressForm.classList.add('form-hidden');
        addressForm.classList.remove('form-visible');
        // Hide after transition
        setTimeout(function () {
          if (document.querySelector('.shipping-option.selected input[type="radio"]')?.value === 'pickup') {
            addressForm.style.display = 'none';
          }
        }, 300);
      }
    }

    // Pickup info card
    if (pickupInfoCard) {
      pickupInfoCard.style.display = isDelivery ? 'none' : 'flex';
    }

    // Toggle required on address fields
    setAddressRequired(isDelivery);

    // Update sidebar summary
    updateSummary(isDelivery);
  }

  if (shippingOptions.length > 0) {
    shippingOptions.forEach(function (opt) {
      opt.addEventListener('click', function () {
        shippingOptions.forEach(function (o) { o.classList.remove('selected'); });
        this.classList.add('selected');

        const radio = this.querySelector('input[type="radio"]');
        if (radio) {
          radio.checked = true;
          applyShippingMethod(radio.value);
        }
      });
    });

    // Init on page load
    const checkedRadio = document.querySelector('.shipping-option input[type="radio"]:checked');
    if (checkedRadio) {
      applyShippingMethod(checkedRadio.value);
    }
  }


  /* ── Payment Method Toggle ──────────────────────────────── */
  const paymentOptions = document.querySelectorAll('.payment-option');

  paymentOptions.forEach(function (opt) {
    opt.addEventListener('click', function () {
      paymentOptions.forEach(function (o) {
        o.classList.remove('selected');
        const check = o.querySelector('.payment-check');
        if (check) check.style.display = 'none';
      });
      this.classList.add('selected');
      const check = this.querySelector('.payment-check');
      if (check) check.style.display = 'flex';

      const radio = this.querySelector('input[type="radio"]');
      if (radio) radio.checked = true;
    });
  });

  // Init payment check icon
  const checkedPayment = document.querySelector('.payment-option input[type="radio"]:checked');
  if (checkedPayment) {
    const parentOpt = checkedPayment.closest('.payment-option');
    if (parentOpt) {
      parentOpt.classList.add('selected');
    }
  }


  /* ── Payment Countdown Timer ─────────────────────────────── */
  const countdownEl = document.getElementById('countdown');
  const timerBarEl  = document.getElementById('timer-bar');

  if (countdownEl) {
    const totalSeconds = 60 * 60; // 1 hour
    const createdAt = new Date(countdownEl.dataset.createdAt).getTime();
    const deadline = createdAt + totalSeconds * 1000;

    function updateTimer() {
      const remaining = Math.max(0, Math.round((deadline - Date.now()) / 1000));
      const hours = Math.floor(remaining / 3600);
      const mins = Math.floor((remaining % 3600) / 60);
      const secs = remaining % 60;
      countdownEl.textContent =
        String(hours).padStart(2, '0') + ':' +
        String(mins).padStart(2, '0') + ':' +
        String(secs).padStart(2, '0');

      if (timerBarEl) {
        timerBarEl.style.width = (remaining / totalSeconds) * 100 + '%';
      }

      if (remaining <= 0) {
        clearInterval(timerInterval);
        countdownEl.textContent = '00:00:00';
        countdownEl.style.color = '#dc2626';
        if (timerBarEl) timerBarEl.style.background = '#dc2626';
      }
    }

    updateTimer();
    const timerInterval = setInterval(updateTimer, 1000);
  }

  /* ── Form Submission (Midtrans Snap) ───────────────────── */
  const checkoutForm = document.querySelector('form.checkout-layout');
  if (checkoutForm) {
    checkoutForm.addEventListener('submit', function (e) {
      const submitBtn = this.querySelector('button[type="submit"]');
      submitBtn.textContent = 'Memproses...';
      submitBtn.disabled = true;
      // Do not prevent default, let the form submit normally
    });
  }

})();
