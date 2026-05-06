/* ============================================================
   NAVBAR.JS — Navigation Interactions
   ============================================================ */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    const nav       = document.querySelector('.site-nav');
    const hamburger = document.querySelector('.nav-hamburger');
    const drawer    = document.querySelector('.nav-drawer');

    /* ── Scroll Shadow ──────────────────────────────────── */
    function onScroll() {
      if (nav) {
        nav.classList.toggle('scrolled', window.scrollY > 20);
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true });

    /* ── Mobile Menu Toggle ─────────────────────────────── */
    if (hamburger && drawer) {
      hamburger.addEventListener('click', function () {
        const isOpen = hamburger.classList.toggle('open');
        drawer.classList.toggle('open', isOpen);

        if (isOpen) {
          drawer.style.display = 'flex';
          requestAnimationFrame(() => drawer.classList.add('open'));
          document.body.style.overflow = 'hidden';
        } else {
          drawer.classList.remove('open');
          document.body.style.overflow = '';
          setTimeout(() => {
            if (!drawer.classList.contains('open')) {
              drawer.style.display = 'none';
            }
          }, 260);
        }
      });

      /* Close drawer on link click */
      drawer.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', () => {
          hamburger.classList.remove('open');
          drawer.classList.remove('open');
          document.body.style.overflow = '';
          setTimeout(() => { drawer.style.display = 'none'; }, 260);
        });
      });

      /* Close on outside click */
      document.addEventListener('click', (e) => {
        if (hamburger.classList.contains('open') &&
            !nav.contains(e.target) &&
            !drawer.contains(e.target)) {
          hamburger.classList.remove('open');
          drawer.classList.remove('open');
          document.body.style.overflow = '';
          setTimeout(() => { drawer.style.display = 'none'; }, 260);
        }
      });
    }

    /* ── Active Link ────────────────────────────────────── */
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a, .nav-drawer a[data-nav]').forEach((link) => {
      if (link.getAttribute('href') === currentPath ||
          (currentPath === '/' && link.getAttribute('href') === '/')) {
        link.classList.add('active');
      }
    });
  });
})();