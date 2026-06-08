/* ============================================================
   register.js — Kahta Grafika Register Page
   Place in: static/js/register.js
   Depends: login.js (must be loaded first)
   ============================================================ */

(function () {
  'use strict';

  /* ── Tiny helper ── */
  function $(id) { return document.getElementById(id); }

  /* ─────────────────────────────────────────
     1. Multi-step navigation
        Step 1: username, email, phone_number, address
        Step 2: password1, password2
     ───────────────────────────────────────── */
  function initMultiStep() {
    const step1Panel = $('step1');
    const step2Panel = $('step2');
    const btnNext    = $('btnNextStep');
    const btnBack    = $('btnBackStep');
    const stepDots   = document.querySelectorAll('.step');
    const stepLine   = document.querySelector('.step-line');

    if (!step1Panel || !step2Panel || !btnNext) return;

    function goStep2() {
      // Validate all step-1 fields before advancing
      const username = $('id_username');
      const email    = $('id_email');
      const phone    = $('id_phone_number');
      const address  = $('id_address');

      const usernameOk = validateNotEmpty(username, 'statusUsername');
      const emailOk    = validateEmailField(email, 'statusEmail');
      const phoneOk    = validatePhoneField(phone, 'statusPhone');
      const addressOk  = validateNotEmpty(address);

      if (!usernameOk || !emailOk || !phoneOk || !addressOk) {
        // Shake the first invalid field group
        const firstInvalid = step1Panel.querySelector('.has-error, .field-group:has(.input-status.invalid)');
        if (firstInvalid) shakeField(firstInvalid);
        return;
      }

      // Advance
      step1Panel.classList.remove('active');
      step2Panel.classList.add('active');

      stepDots[0].classList.add('done');
      stepDots[0].classList.remove('active');
      stepDots[1].classList.add('active');
      if (stepLine) stepLine.classList.add('filled');

      const firstInput = step2Panel.querySelector('input');
      if (firstInput) setTimeout(() => firstInput.focus(), 60);
    }

    function goStep1() {
      step2Panel.classList.remove('active');
      step1Panel.classList.add('active');

      stepDots[0].classList.remove('done');
      stepDots[0].classList.add('active');
      stepDots[1].classList.remove('active');
      if (stepLine) stepLine.classList.remove('filled');

      const firstInput = step1Panel.querySelector('input');
      if (firstInput) setTimeout(() => firstInput.focus(), 60);
    }

    btnNext.addEventListener('click', goStep2);
    if (btnBack) btnBack.addEventListener('click', goStep1);

    // Enter key on step-1 inputs advances the step (except textarea uses Enter naturally)
    step1Panel.querySelectorAll('input').forEach(input => {
      input.addEventListener('keydown', e => {
        if (e.key === 'Enter') { e.preventDefault(); goStep2(); }
      });
    });
  }

  /* ─────────────────────────────────────────
     2. Field validators
     ───────────────────────────────────────── */

  function validateNotEmpty(input, statusId) {
    if (!input) return false;
    const ok = input.value.trim().length > 0;
    const group = input.closest('.field-group');
    if (group) group.classList.toggle('has-error', !ok);
    if (statusId) setInputStatus(statusId, ok ? 'valid' : 'invalid');
    return ok;
  }

  function validateEmailField(input, statusId) {
    if (!input) return true; // email might be optional depending on model
    const val = input.value.trim();
    if (!val) {
      setInputStatus(statusId, 'invalid');
      input.closest('.field-group')?.classList.add('has-error');
      return false;
    }
    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
    setInputStatus(statusId, ok ? 'valid' : 'invalid');
    input.closest('.field-group')?.classList.toggle('has-error', !ok);
    return ok;
  }

  function validatePhoneField(input, statusId) {
    if (!input) return true;
    const val = input.value.trim().replace(/[\s\-().]/g, '');
    // Accept Indonesian formats: 08xx, +628xx, 628xx — min 8 digits
    const ok = val.length >= 8 && /^(\+?62|0)\d{7,}$/.test(val);
    setInputStatus(statusId, val ? (ok ? 'valid' : 'invalid') : 'invalid');
    input.closest('.field-group')?.classList.toggle('has-error', !ok);
    return ok;
  }

  function setInputStatus(statusId, state) {
    const el = $(statusId);
    if (!el) return;
    el.className = 'input-status';
    el.textContent = '';
    if (state === 'valid')   { el.classList.add('valid');   el.textContent = '✓'; }
    if (state === 'invalid') { el.classList.add('invalid'); el.textContent = '✕'; }
  }

  function shakeField(group) {
    if (!group) return;
    group.classList.add('shake');
    group.addEventListener('animationend', () => group.classList.remove('shake'), { once: true });
  }

  /* ─────────────────────────────────────────
     3. Live validation on step-1 inputs
     ───────────────────────────────────────── */
  function initLiveValidation() {
    const pairs = [
      { id: 'id_username',     statusId: 'statusUsername', fn: (el) => validateNotEmpty(el, 'statusUsername') },
      { id: 'id_email',        statusId: 'statusEmail',    fn: (el) => validateEmailField(el, 'statusEmail') },
      { id: 'id_phone_number', statusId: 'statusPhone',    fn: (el) => validatePhoneField(el, 'statusPhone') },
    ];

    pairs.forEach(({ id, fn }) => {
      const el = $(id);
      if (!el) return;
      el.addEventListener('blur',  () => fn(el));
      el.addEventListener('input', () => { if (el.value.length > 0) fn(el); });
    });

    // Phone: auto-format as user types (insert hyphens)
    const phone = $('id_phone_number');
    if (phone) {
      phone.addEventListener('input', function () {
        // Keep raw digits / leading + sign
        let raw = phone.value.replace(/[^\d+]/g, '');
        // Limit length
        if (raw.startsWith('+')) raw = '+' + raw.slice(1, 15);
        else raw = raw.slice(0, 14);
        phone.value = raw;
      });
    }
  }

  /* ─────────────────────────────────────────
     4. Password strength meter
     ───────────────────────────────────────── */
  const STRENGTH_RULES = [
    { id: 'length',  test: v => v.length >= 8 },
    { id: 'number',  test: v => /\d/.test(v) },
    { id: 'upper',   test: v => /[A-Z]/.test(v) },
    { id: 'special', test: v => /[^a-zA-Z0-9]/.test(v) },
  ];

  const STRENGTH_MAP = [
    { cls: '',       label: '' },
    { cls: 'weak',   label: 'Lemah' },
    { cls: 'fair',   label: 'Cukup' },
    { cls: 'good',   label: 'Bagus' },
    { cls: 'strong', label: 'Kuat'  },
  ];

  function initPasswordStrength() {
    const input         = $('id_password1');
    const strengthBar   = $('strengthBar');
    const strengthFill  = $('strengthFill');
    const strengthLabel = $('strengthLabel');
    const ruleItems     = document.querySelectorAll('.rule');

    if (!input || !strengthFill) return;

    input.addEventListener('input', function () {
      const val = input.value;

      if (strengthBar) strengthBar.classList.toggle('visible', val.length > 0);

      let score = 0;
      STRENGTH_RULES.forEach((rule, i) => {
        const pass = rule.test(val);
        if (pass) score++;
        if (ruleItems[i]) ruleItems[i].classList.toggle('pass', pass);
      });

      const s = val.length === 0 ? 0 : score;
      const { cls, label } = STRENGTH_MAP[s];
      strengthFill.className  = 'strength-fill'  + (cls ? ' ' + cls : '');
      strengthLabel.className = 'strength-label' + (cls ? ' ' + cls : '');
      strengthLabel.textContent = label;
    });
  }

  /* ─────────────────────────────────────────
     5. Password match feedback
     ───────────────────────────────────────── */
  function initPasswordMatch() {
    const p1   = $('id_password1');
    const p2   = $('id_password2');
    const hint = $('matchHint');

    if (!p1 || !p2 || !hint) return;

    function check() {
      if (!p2.value) { hint.textContent = ''; hint.className = 'match-hint'; return; }
      const match = p1.value === p2.value;
      hint.textContent = match ? '✓ Password cocok' : '✕ Password tidak cocok';
      hint.className   = 'match-hint ' + (match ? 'match' : 'no-match');
    }

    p1.addEventListener('input', check);
    p2.addEventListener('input', check);
  }

  /* ─────────────────────────────────────────
     6. Form submit with client-side guards
     ───────────────────────────────────────── */
  function initFormSubmit() {
    const form  = $('registerForm');
    const btn   = $('submitBtn');
    const terms = $('termsCheck');

    if (!form || !btn) return;

    form.addEventListener('submit', function (e) {
      // Terms checkbox
      if (terms && !terms.checked) {
        e.preventDefault();
        shakeField(terms.closest('label'));
        return;
      }

      // Passwords match
      const p1 = $('id_password1');
      const p2 = $('id_password2');
      if (p1 && p2 && p1.value !== p2.value) {
        e.preventDefault();
        shakeField(p2.closest('.field-group'));
        return;
      }

      btn.classList.add('is-loading');
      btn.disabled = true;

      // Safety re-enable after 10 s
      setTimeout(() => { btn.classList.remove('is-loading'); btn.disabled = false; }, 10_000);
    });
  }

  /* ─────────────────────────────────────────
     7. If Django returned errors, reveal the
        correct step so errors are visible
     ───────────────────────────────────────── */
  function initErrorStep() {
    const step2HasError =
      document.querySelector('#step2 .field-error') ||
      document.querySelector('#step2 .has-error');

    if (!step2HasError) return;

    const step1    = $('step1');
    const step2    = $('step2');
    const stepDots = document.querySelectorAll('.step');
    const stepLine = document.querySelector('.step-line');

    if (step1 && step2) {
      step1.classList.remove('active');
      step2.classList.add('active');
      stepDots[0].classList.add('done');
      stepDots[0].classList.remove('active');
      stepDots[1].classList.add('active');
      if (stepLine) stepLine.classList.add('filled');
    }
  }

  /* ── Bootstrap ── */
  document.addEventListener('DOMContentLoaded', function () {
    initMultiStep();
    initLiveValidation();
    initPasswordStrength();
    initPasswordMatch();
    initFormSubmit();
    initErrorStep();
  });

})();