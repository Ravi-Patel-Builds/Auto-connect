document.addEventListener('DOMContentLoaded', () => {
  const counters = [
    { id: 'cnt-drivers', end: 12, suffix: '+' },
    { id: 'cnt-rides', end: 200, suffix: '+' },
    { id: 'cnt-reviews', end: 150, suffix: '+' }
  ];

  counters.forEach(({ id, end, suffix }) => {
    const el = document.getElementById(id);
    if (!el) return;
    let current = 0;
    const step = Math.max(1, Math.floor(end / 50));
    const interval = setInterval(() => {
      current += step;
      if (current >= end) {
        current = end;
        clearInterval(interval);
      }
      el.textContent = `${current}${suffix}`;
    }, 20);
  });

  const navToggle = document.querySelector('.nav-toggle');
  const navMenu = document.querySelector('.main-nav');
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navMenu.classList.toggle('open');
    });
  }

  const fbForm = document.querySelector('#feedbackForm');
  if (fbForm) {
    fbForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const formData = new URLSearchParams(new FormData(fbForm));
      try {
        const response = await fetch('/feedback', { method: 'POST', body: formData });
        const result = await response.json();
        if (result.status === 'success') {
          alert('Thanks — feedback received!');
          fbForm.reset();
        } else {
          alert('Something went wrong.');
        }
      } catch (error) {
        alert('Network error. Please try again.');
      }
    });
  }
});


