document.documentElement.classList.add('bg-js');

function getIncludeBase() {
  const script = document.querySelector('script[src*="includes.js"]');
  if (!script || !script.src) return `${window.location.origin}/`;
  return script.src.replace(/includes\.js(?:\?.*)?$/, '');
}

async function injectPartial(id, file) {
  const el = document.getElementById(id);
  if (!el) return;
  try {
    const res = await fetch(`${getIncludeBase()}${file}`);
    if (!res.ok) throw new Error(res.statusText);
    el.outerHTML = await res.text();
  } catch (err) {
    console.warn('Include failed:', file, err);
  }
}

function closeAllDropdowns() {
  document.querySelectorAll('.nav-dropdown-wrap.open').forEach((w) => {
    w.classList.remove('open');
    const b = w.querySelector('.nav-dropdown-btn');
    if (b) b.setAttribute('aria-expanded', 'false');
  });
}

function isMobileNav() {
  return window.matchMedia('(max-width: 980px)').matches;
}

function blurNavFocus() {
  const active = document.activeElement;
  if (active && active.closest && active.closest('.site-nav')) {
    active.blur();
  }
}

function initNav() {
  const btn = document.getElementById('hamburger-btn');
  const nav = document.getElementById('site-nav') || document.querySelector('.site-nav');
  const header = document.querySelector('.site-header');

  if (btn && nav) {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (!open) closeAllDropdowns();
    });
  }

  document.querySelectorAll('.nav-dropdown-wrap').forEach((wrap) => {
    const b = wrap.querySelector('.nav-dropdown-btn');
    if (!b) return;

    b.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      // Desktop: hover/focus-visible opens menus. Click must not leave sticky :focus-within.
      if (!isMobileNav()) {
        b.blur();
        return;
      }
      const willOpen = !wrap.classList.contains('open');
      closeAllDropdowns();
      if (willOpen) {
        wrap.classList.add('open');
        b.setAttribute('aria-expanded', 'true');
      }
    });

    // Clear focus when pointer leaves so menus don't stick open via :focus-within
    wrap.addEventListener('mouseleave', () => {
      if (!isMobileNav()) {
        const focused = wrap.querySelector(':focus');
        if (focused) focused.blur();
      }
    });
  });

  // Close when clicking a menu link
  document.querySelectorAll('.nav-dropdown-menu a').forEach((a) => {
    a.addEventListener('click', () => {
      closeAllDropdowns();
      blurNavFocus();
      if (nav) nav.classList.remove('open');
      if (btn) btn.setAttribute('aria-expanded', 'false');
    });
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (header && header.contains(e.target)) {
      if (!e.target.closest('.nav-dropdown-wrap')) {
        closeAllDropdowns();
        blurNavFocus();
      }
      return;
    }
    closeAllDropdowns();
    blurNavFocus();
    if (nav) nav.classList.remove('open');
    if (btn) btn.setAttribute('aria-expanded', 'false');
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAllDropdowns();
      blurNavFocus();
      if (nav) nav.classList.remove('open');
      if (btn) btn.setAttribute('aria-expanded', 'false');
    }
  });

  // Leave desktop hover/open state clean when resizing
  window.addEventListener('resize', () => {
    if (!isMobileNav()) {
      closeAllDropdowns();
      blurNavFocus();
      if (nav) nav.classList.remove('open');
      if (btn) btn.setAttribute('aria-expanded', 'false');
    }
  });
}

function markActiveNav() {
  const path = location.pathname.replace(/index\.html$/, '');
  document.querySelectorAll('.site-nav > a[href]').forEach((a) => {
    try {
      const href = new URL(a.getAttribute('href'), location.origin).pathname;
      if (href !== '/' && path.startsWith(href)) a.classList.add('active');
      if (href === '/' && (path === '/' || path === '' || /\/breakinggroundlsad-website\/?$/.test(path))) {
        a.classList.add('active');
      }
    } catch (_) { /* ignore */ }
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  await Promise.all([
    injectPartial('site-header-include', 'header.html'),
    injectPartial('site-footer-include', 'footer.html'),
  ]);
  initNav();
  markActiveNav();
});
