(function bootHome() {
  function run() {
    initHeroSlider();
    initReveals();
    initForms();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();

function initReveals() {
  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('is-visible');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('is-visible'));
  }
}

function initForms() {
  document.querySelectorAll('form[data-bg-form]').forEach((form) => {
    const pageField = form.querySelector('[name="page"]');
    if (pageField) pageField.value = location.pathname;
  });
}

function initHeroSlider() {
  const slides = document.querySelectorAll('.hero-slide');
  if (slides.length < 2) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (document.documentElement.dataset.heroSlider === '1') return;
  document.documentElement.dataset.heroSlider = '1';

  let current = 0;
  let slideInterval = null;

  function goTo(index) {
    const prevBg = slides[current].querySelector('.hero-slide-bg');
    slides[current].classList.remove('active');
    if (prevBg) {
      prevBg.style.animation = 'none';
      void prevBg.offsetWidth;
      prevBg.style.animation = '';
    }

    current = (index + slides.length) % slides.length;
    slides[current].classList.add('active');

    const newBg = slides[current].querySelector('.hero-slide-bg');
    if (newBg) {
      newBg.style.animation = 'none';
      void newBg.offsetWidth;
      newBg.style.animation = '';
    }
  }

  function startSlider() {
    if (slideInterval) clearInterval(slideInterval);
    slideInterval = setInterval(() => goTo(current + 1), 6000);
  }

  startSlider();

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      if (slideInterval) clearInterval(slideInterval);
      slideInterval = null;
    } else {
      startSlider();
    }
  });
}
