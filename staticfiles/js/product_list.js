/* ─── catalog.js ──────────────────────────────────────────────────── */
'use strict';

document.addEventListener('DOMContentLoaded', () => {

  /* ── Price slider ──────────────────────────────────────────────── */
  const slider = document.getElementById('price-slider');
  const sliderVal = document.getElementById('price-slider-val');

  if (slider && sliderVal) {
    const updateSlider = () => {
      const pct = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
      slider.style.background =
        `linear-gradient(to right, var(--amber) 0%, var(--amber) ${pct}%, var(--border) ${pct}%)`;
      sliderVal.textContent = `Rp ${Number(slider.value).toLocaleString('id-ID')}+`;
    };
    slider.addEventListener('input', updateSlider);
    updateSlider();
  }

  /* ── Add-to-cart buttons ───────────────────────────────────────── */
  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }

  document.querySelectorAll('.btn-cart').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      const productName = this.dataset.productName || 'Produk';

      // Call backend
      fetch('/cart/add/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
      })
        .then(r => {
          if (r.status === 403 || r.redirected) {
            // Not logged in — redirect to login
            window.location.href = '/auth/login/?next=' + encodeURIComponent(window.location.pathname);
            return null;
          }
          return r.json();
        })
        .then(data => {
          if (!data) return;

          if (data.success) {
            // Visual feedback on button
            this.classList.add('added');
            this.innerHTML = `
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Ditambahkan!`;

            showToast(data.message || `${productName} ditambahkan ke keranjang`);

            // Update navbar badge
            let badge = document.getElementById('cart-badge');
            if (badge) {
              badge.textContent = data.item_count;
            } else {
              const cartLink = document.querySelector('.nav-cart-link');
              if (cartLink) {
                badge = document.createElement('span');
                badge.className = 'nav-cart-badge';
                badge.id = 'cart-badge';
                badge.textContent = data.item_count;
                cartLink.appendChild(badge);
              }
            }

            // Reset button after 2s
            setTimeout(() => {
              this.classList.remove('added');
              this.innerHTML = `
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
                  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
                </svg>
                Tambah ke Keranjang`;
            }, 2000);
          }
        })
        .catch(() => {
          showToast('Gagal menambahkan ke keranjang');
        });
    });
  });

  /* ── Sort select → auto submit ─────────────────────────────────── */
  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      const url = new URL(window.location.href);
      url.searchParams.set('sort', sortSelect.value);
      url.searchParams.delete('page');
      window.location.href = url.toString();
    });
  }

  /* ── Filter form: include sort param on submit ─────────────────── */
  const filterForm = document.getElementById('filter-form');
  if (filterForm) {
    filterForm.addEventListener('submit', (e) => {
      // Add sort value as hidden input if sort is set
      const currentSort = new URL(window.location.href).searchParams.get('sort');
      if (currentSort) {
        let hidden = filterForm.querySelector('input[name="sort"]');
        if (!hidden) {
          hidden = document.createElement('input');
          hidden.type = 'hidden';
          hidden.name = 'sort';
          filterForm.appendChild(hidden);
        }
        hidden.value = currentSort;
      }

      // Remove empty fields to keep URL clean
      filterForm.querySelectorAll('input, select').forEach(el => {
        if (el.type === 'radio' && !el.checked) return;
        if (el.value === '' || el.value === '10000') {
          el.disabled = true;
        }
      });
    });
  }

});

/* ── Toast helper ──────────────────────────────────────────────────── */
function showToast(msg) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    Object.assign(container.style, {
      position: 'fixed',
      bottom: '28px',
      right: '28px',
      zIndex: '9999',
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
    });
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.textContent = msg;
  Object.assign(toast.style, {
    background: '#2c1a0e',
    color: '#fff',
    padding: '12px 20px',
    borderRadius: '10px',
    fontSize: '13.5px',
    fontFamily: "'DM Sans', sans-serif",
    boxShadow: '0 4px 18px rgba(0,0,0,.18)',
    opacity: '0',
    transform: 'translateY(10px)',
    transition: 'opacity .25s ease, transform .25s ease',
    maxWidth: '280px',
    lineHeight: '1.4',
  });

  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
  });

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(6px)';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}