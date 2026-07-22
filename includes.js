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

function initNav() {
  const btn = document.getElementById('hamburger-btn');
  const nav = document.querySelector('.site-nav');
  if (btn && nav) {
    btn.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  document.querySelectorAll('.nav-dropdown-btn').forEach((b) => {
    b.addEventListener('click', () => {
      b.parentElement.classList.toggle('open');
    });
  });
}

function markActiveNav() {
  const path = location.pathname.replace(/index\.html$/, '');
  document.querySelectorAll('.site-nav a[href]').forEach((a) => {
    try {
      const href = new URL(a.getAttribute('href'), location.origin).pathname;
      if (href !== '/' && path.startsWith(href)) a.classList.add('active');
      if (href === '/' && (path === '/' || path === '')) a.classList.add('active');
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
