/* ============================================================
   HOME.JS — Home Page Interactions
   ============================================================ */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    /* ── Hero entrance animation ──────────────────────────── */
    const heroContent = document.querySelector('.hero-content');
    const heroVisual  = document.querySelector('.hero-visual');

    if (heroContent) {
      heroContent.style.opacity = '0';
      heroContent.style.transform = 'translateY(24px)';
      requestAnimationFrame(() => {
        heroContent.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
        setTimeout(() => {
          heroContent.style.opacity = '1';
          heroContent.style.transform = 'translateY(0)';
        }, 80);
      });
    }

    if (heroVisual) {
      heroVisual.style.opacity = '0';
      heroVisual.style.transform = 'translateY(18px) scale(0.97)';
      requestAnimationFrame(() => {
        heroVisual.style.transition = 'opacity 0.8s ease 0.25s, transform 0.8s ease 0.25s';
        setTimeout(() => {
          heroVisual.style.opacity = '1';
          heroVisual.style.transform = 'translateY(0) scale(1)';
        }, 100);
      });
    }

    /* ── Step number hover effect ─────────────────────────── */
    document.querySelectorAll('.step').forEach((step) => {
      const num = step.querySelector('.step-number');
      step.addEventListener('mouseenter', () => {
        if (num) {
          num.style.background = 'var(--color-accent)';
          num.style.transform = 'scale(1.1)';
        }
      });
      step.addEventListener('mouseleave', () => {
        if (num) {
          num.style.background = 'var(--color-primary)';
          num.style.transform = 'scale(1)';
        }
      });
    });

    /* ── Smooth step number transitions ───────────────────── */
    document.querySelectorAll('.step-number').forEach((num) => {
      num.style.transition = 'background 0.25s ease, transform 0.25s ease';
    });

  });
})();