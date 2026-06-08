/* ============================================================
   CART.JS — Cart Page Interactions
   ============================================================ */

(function () {
  'use strict';

  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }

  function formatRupiah(num) {
    return 'Rp ' + Number(num).toLocaleString('id-ID');
  }

  /* ── Quantity Buttons ────────────────────────────────────── */
  document.querySelectorAll('.qty-minus, .qty-plus').forEach((btn) => {
    btn.addEventListener('click', function () {
      const itemId = this.dataset.itemId;
      const qtyEl = document.getElementById('qty-' + itemId);
      let qty = parseInt(qtyEl.textContent);

      if (this.classList.contains('qty-minus')) {
        qty = Math.max(1, qty - 1);
      } else {
        qty += 1;
      }

      qtyEl.textContent = qty;

      fetch('/cart/update/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ item_id: itemId, quantity: qty }),
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.success) {
            document.getElementById('subtotal-' + itemId).textContent = formatRupiah(data.subtotal);
            document.getElementById('cart-subtotal').textContent = formatRupiah(data.total);
            document.getElementById('cart-total').textContent = formatRupiah(data.total);
          }
        });
    });
  });

  /* ── Remove Buttons ──────────────────────────────────────── */
  document.querySelectorAll('.cart-item-remove').forEach((btn) => {
    btn.addEventListener('click', function () {
      const itemId = this.dataset.itemId;
      const itemEl = this.closest('.cart-item');

      fetch('/cart/remove/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ item_id: itemId }),
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.success) {
            itemEl.style.transition = 'all 0.3s ease';
            itemEl.style.opacity = '0';
            itemEl.style.transform = 'translateX(-20px)';
            setTimeout(() => {
              itemEl.remove();
              document.getElementById('cart-subtotal').textContent = formatRupiah(data.total);
              document.getElementById('cart-total').textContent = formatRupiah(data.total);

              if (data.item_count === 0) {
                location.reload();
              }
            }, 300);
          }
        });
    });
  });
})();
