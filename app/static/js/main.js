/**
 * BOOKGLAM — Global JavaScript
 * Handles: page loader, scroll reveal, counters, ripples,
 *          mobile sidebars (admin + dashboard), nav, modals,
 *          form enhancements, toast notifications
 */

/* ============================================================
   1. PAGE LOADER
   ============================================================ */
(function () {
  const loader = document.getElementById('page-loader');
  if (!loader) return;
  window.addEventListener('load', () => {
    setTimeout(() => loader.classList.add('hidden'), 250);
  });
  // Show loader on navigation away
  document.querySelectorAll('a[href]').forEach(link => {
    link.addEventListener('click', e => {
      const href = link.getAttribute('href');
      if (!href || href.startsWith('#') || href.startsWith('javascript') ||
          href.startsWith('mailto') || link.target === '_blank') return;
      loader.classList.remove('hidden');
    });
  });
})();

/* ============================================================
   2. SCROLL REVEAL (IntersectionObserver)
   ============================================================ */
(function () {
  const els = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  if (!els.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  els.forEach(el => io.observe(el));
})();

/* ============================================================
   3. ANIMATED NUMBER COUNTERS
   ============================================================ */
(function () {
  function animateCount(el) {
    const target = parseFloat(el.dataset.target || el.textContent.replace(/[^0-9.]/g, ''));
    const prefix = el.dataset.prefix || '';
    const suffix = el.dataset.suffix || '';
    const isFloat = String(target).includes('.');
    const duration = 1400;
    const start = performance.now();
    const easeOut = t => 1 - Math.pow(1 - t, 3);
    function step(now) {
      const progress = Math.min((now - start) / duration, 1);
      const val = target * easeOut(progress);
      el.textContent = prefix + (isFloat ? val.toFixed(1) : Math.floor(val).toLocaleString()) + suffix;
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = prefix + (isFloat ? target.toFixed(1) : target.toLocaleString()) + suffix;
    }
    requestAnimationFrame(step);
  }

  const counters = document.querySelectorAll('.count-up, [data-countup]');
  if (!counters.length) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { animateCount(e.target); io.unobserve(e.target); }
    });
  }, { threshold: 0.5 });
  counters.forEach(el => io.observe(el));
})();

/* ============================================================
   4. RIPPLE EFFECT on buttons
   ============================================================ */
(function () {
  document.addEventListener('click', e => {
    const btn = e.target.closest('.btn-gold, .btn-outline-gold');
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height) * 2;
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top  - size / 2;
    const ripple = document.createElement('span');
    ripple.className = 'ripple';
    ripple.style.cssText = `width:${size}px;height:${size}px;left:${x}px;top:${y}px;`;
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });
})();

/* ============================================================
   5. MOBILE SIDEBAR — Admin
   ============================================================ */
(function () {
  const sidebar  = document.getElementById('admin-sidebar');
  const overlay  = document.getElementById('admin-sidebar-overlay');
  const hamburger = document.getElementById('admin-hamburger');
  if (!sidebar || !hamburger) return;

  function openSidebar()  { sidebar.classList.add('open');  overlay && overlay.classList.add('active'); document.body.style.overflow = 'hidden'; }
  function closeSidebar() { sidebar.classList.remove('open'); overlay && overlay.classList.remove('active'); document.body.style.overflow = ''; }

  hamburger.addEventListener('click', () => sidebar.classList.contains('open') ? closeSidebar() : openSidebar());
  overlay && overlay.addEventListener('click', closeSidebar);

  // Close on escape
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSidebar(); });
})();

/* ============================================================
   6. MOBILE SIDEBAR — Client / Provider Dashboard
   ============================================================ */
(function () {
  const sidebar   = document.getElementById('dash-sidebar');
  const overlay   = document.getElementById('dash-sidebar-overlay');
  const hamburger = document.getElementById('dash-hamburger');
  if (!sidebar || !hamburger) return;

  function openSidebar()  { sidebar.classList.add('open');  overlay && overlay.classList.add('active'); document.body.style.overflow = 'hidden'; }
  function closeSidebar() { sidebar.classList.remove('open'); overlay && overlay.classList.remove('active'); document.body.style.overflow = ''; }

  hamburger.addEventListener('click', () => sidebar.classList.contains('open') ? closeSidebar() : openSidebar());
  overlay && overlay.addEventListener('click', closeSidebar);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSidebar(); });
})();

/* ============================================================
   7. PUBLIC NAV — scroll shadow + mobile menu
   ============================================================ */
(function () {
  const nav = document.getElementById('public-nav');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.style.boxShadow = window.scrollY > 10
      ? '0 4px 24px rgba(26,20,16,0.1)'
      : 'none';
  }, { passive: true });
})();

/* ============================================================
   8. SMOOTH FLASH MESSAGE DISMISS
   ============================================================ */
(function () {
  document.querySelectorAll('.flash-success,.flash-danger,.flash-info,.flash-warning').forEach(el => {
    // Auto-dismiss after 5s
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s, transform 0.4s, max-height 0.4s, padding 0.4s, margin 0.4s';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      setTimeout(() => el.remove(), 420);
    }, 5000);
  });
})();

/* ============================================================
   9. TOAST NOTIFICATION SYSTEM (global helper)
   ============================================================ */
window.BG = window.BG || {};
BG.toast = function (message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:10px;';
    document.body.appendChild(container);
  }
  const colors = { success: '#10b981', danger: '#ef4444', info: '#3b82f6', warning: '#f59e0b' };
  const icons  = { success: 'fa-check-circle', danger: 'fa-times-circle', info: 'fa-info-circle', warning: 'fa-exclamation-circle' };
  const toast = document.createElement('div');
  toast.style.cssText = `
    background:#fff; border-left:4px solid ${colors[type]||colors.info};
    padding:12px 18px 12px 14px; border-radius:6px;
    box-shadow:0 8px 32px rgba(0,0,0,0.12); display:flex; align-items:center; gap:10px;
    font-family:'DM Sans',sans-serif; font-size:0.875rem; min-width:260px; max-width:360px;
    animation:slideToast 0.35s cubic-bezier(.22,1,.36,1);
  `;
  toast.innerHTML = `
    <i class="fas ${icons[type]||icons.info}" style="color:${colors[type]||colors.info};flex-shrink:0;"></i>
    <span style="flex:1;color:#1A1410;">${message}</span>
    <button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;color:#9ca3af;font-size:1rem;padding:0;line-height:1;">✕</button>
  `;
  if (!document.querySelector('#toast-keyframes')) {
    const s = document.createElement('style');
    s.id = 'toast-keyframes';
    s.textContent = `@keyframes slideToast{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}`;
    document.head.appendChild(s);
  }
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = 'opacity 0.3s, transform 0.3s';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    setTimeout(() => toast.remove(), 320);
  }, duration);
};

/* ============================================================
   10. SMOOTH MODAL SYSTEM
   ============================================================ */
BG.openModal = function (id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.remove('hidden');
  const inner = modal.querySelector('.modal-inner');
  if (inner) inner.classList.add('modal-enter');
  modal.classList.add('modal-backdrop-enter');
  document.body.style.overflow = 'hidden';
};
BG.closeModal = function (id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.add('hidden');
  document.body.style.overflow = '';
};
// Wire up data-modal-open / data-modal-close attrs
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => BG.openModal(btn.dataset.modalOpen));
  });
  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', () => BG.closeModal(btn.dataset.modalClose));
  });
  // Close on backdrop click
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', e => {
      if (e.target === backdrop) BG.closeModal(backdrop.id);
    });
  });
});

/* ============================================================
   11. TABLE ROW HOVER + SORTABLE COLUMN HIGHLIGHT
   ============================================================ */
(function () {
  document.querySelectorAll('tbody tr').forEach(row => {
    row.style.cursor = 'default';
    row.addEventListener('mouseenter', () => row.style.transition = 'background 0.18s');
  });
})();

/* ============================================================
   12. FORM: Auto-resize textarea
   ============================================================ */
document.querySelectorAll('textarea[data-autoresize]').forEach(ta => {
  ta.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 200) + 'px';
  });
});

/* ============================================================
   13. CARD TILT EFFECT (subtle, public pages only)
   ============================================================ */
(function () {
  document.querySelectorAll('.card-tilt').forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width  - 0.5) * 10;
      const y = ((e.clientY - rect.top)  / rect.height - 0.5) * -10;
      card.style.transform = `perspective(600px) rotateX(${y}deg) rotateY(${x}deg) translateY(-4px)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transition = 'transform 0.5s ease';
      card.style.transform = '';
    });
    card.addEventListener('mouseenter', () => { card.style.transition = 'transform 0.1s ease'; });
  });
})();

/* ============================================================
   14. PROGRESS BAR (top of page on link click)
   ============================================================ */
(function () {
  const bar = document.getElementById('nprogress-bar');
  if (!bar) return;
  let timer;
  document.querySelectorAll('a[href]').forEach(link => {
    link.addEventListener('click', e => {
      const href = link.getAttribute('href');
      if (!href || href.startsWith('#') || href.startsWith('javascript') || link.target === '_blank') return;
      bar.style.width = '0%';
      bar.style.opacity = '1';
      clearTimeout(timer);
      // Simulate progress
      let w = 0;
      const interval = setInterval(() => {
        w += Math.random() * 18;
        if (w >= 85) { clearInterval(interval); w = 85; }
        bar.style.width = w + '%';
      }, 120);
      timer = setTimeout(() => {
        clearInterval(interval);
        bar.style.width = '100%';
        setTimeout(() => { bar.style.opacity = '0'; bar.style.width = '0%'; }, 300);
      }, 3000);
    });
  });
})();

/* ============================================================
   15. DASHBOARD — stat cards count-up on load
   ============================================================ */
(function () {
  document.querySelectorAll('[data-stat]').forEach(el => {
    const raw = el.textContent.trim();
    const num = parseFloat(raw.replace(/[^0-9.]/g, ''));
    if (isNaN(num)) return;
    el.dataset.target = num;
    el.dataset.prefix = raw.includes('₦') ? '₦' : '';
    el.dataset.suffix = '';
    el.classList.add('count-up');
    el.textContent = el.dataset.prefix + '0';
  });
})();

/* ============================================================
   16. ACTIVE NAV LINK HIGHLIGHT (auto based on URL)
   ============================================================ */
(function () {
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && path.startsWith(href) && href !== '/') {
      link.classList.add('active');
    }
  });
})();

/* ============================================================
   17. TABLE SEARCH FILTER
   ============================================================ */
BG.filterTable = function (inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;
  input.addEventListener('input', () => {
    const q = input.value.toLowerCase();
    table.querySelectorAll('tbody tr').forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  });
};

/* ============================================================
   18. BOOKING STATUS POLLING (client tracking page)
      Refreshes status badge every 30s without full reload
   ============================================================ */
BG.pollStatus = function (bookingId, badgeEl) {
  if (!badgeEl) return;
  setInterval(async () => {
    try {
      const res = await fetch(`/client/bookings/${bookingId}/status`);
      if (res.ok) {
        const data = await res.json();
        badgeEl.textContent = data.status.replace(/_/g, ' ');
        badgeEl.className = `status-badge status-${data.status}`;
      }
    } catch (_) {}
  }, 30000);
};

/* ============================================================
   19. SMOOTH ACCORDION (how-it-works etc.)
   ============================================================ */
document.querySelectorAll('[data-accordion-toggle]').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = document.getElementById(btn.dataset.accordionToggle);
    if (!target) return;
    const isOpen = !target.classList.contains('accordion-hidden');
    // Close all
    document.querySelectorAll('.accordion-panel').forEach(p => {
      p.style.maxHeight = '0';
      p.classList.add('accordion-hidden');
    });
    if (!isOpen) {
      target.classList.remove('accordion-hidden');
      target.style.maxHeight = target.scrollHeight + 'px';
    }
  });
});

/* ============================================================
   20. COPY TO CLIPBOARD helper
   ============================================================ */
BG.copy = function (text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    if (btn) {
      const orig = btn.innerHTML;
      btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
      setTimeout(() => btn.innerHTML = orig, 2000);
    }
    BG.toast('Copied to clipboard', 'success', 2000);
  });
};
