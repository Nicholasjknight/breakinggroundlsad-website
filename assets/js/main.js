document.addEventListener('DOMContentLoaded', () => {
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

  document.querySelectorAll('form[data-bg-form]').forEach((form) => {
    const pageField = form.querySelector('[name="page"]');
    if (pageField) pageField.value = location.pathname;
  });
});
