/* ============================================
   PARTICLE CANVAS BACKGROUND
   ============================================ */
const canvas = document.getElementById('bg-canvas');
const isMobile = window.matchMedia('(max-width: 768px)').matches;
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (!isMobile && !prefersReduced) {
  const ctx = canvas.getContext('2d');
  let particles = [];
  const mouse = { x: -9999, y: -9999 };

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', () => { resize(); initParticles(); });
  window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });

  function initParticles() {
    particles = [];
    const count = Math.floor((window.innerWidth * window.innerHeight) / 14000);
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        r: Math.random() * 1.5 + 0.5,
        opacity: Math.random() * 0.5 + 0.1,
      });
    }
  }
  initParticles();

  function drawParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0) p.x = canvas.width;
      if (p.x > canvas.width) p.x = 0;
      if (p.y < 0) p.y = canvas.height;
      if (p.y > canvas.height) p.y = 0;

      // Mouse repulsion
      const dx = p.x - mouse.x;
      const dy = p.y - mouse.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 120) {
        const force = (120 - dist) / 120;
        p.x += dx * force * 0.03;
        p.y += dy * force * 0.03;
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(124,106,247,${p.opacity})`;
      ctx.fill();

      // Connect nearby particles
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx2 = p.x - p2.x;
        const dy2 = p.y - p2.y;
        const d = Math.sqrt(dx2 * dx2 + dy2 * dy2);
        if (d < 100) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(124,106,247,${0.12 * (1 - d / 100)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(drawParticles);
  }
  drawParticles();
}

/* ============================================
   NAV SCROLL EFFECT
   ============================================ */
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  if (window.scrollY > 40) {
    nav.classList.add('scrolled');
  } else {
    nav.classList.remove('scrolled');
  }
}, { passive: true });

/* ============================================
   SCROLL REVEAL
   ============================================ */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

/* ============================================
   TYPING TERMINAL EFFECT
   ============================================ */
function typeTerminal(terminal) {
  const lines = terminal.querySelectorAll('.terminal-line');
  let delay = 200;

  lines.forEach(line => {
    line.style.opacity = '0';
    line.style.transform = 'translateX(-6px)';

    setTimeout(() => {
      line.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
      line.style.opacity = '1';
      line.style.transform = 'translateX(0)';
    }, delay);

    const text = line.textContent.trim();
    delay += text ? Math.min(text.length * 6, 180) : 60;
  });
}

const terminalObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !entry.target.dataset.typed) {
      entry.target.dataset.typed = 'true';
      setTimeout(() => typeTerminal(entry.target), 200);
    }
  });
}, { threshold: 0.3 });

document.querySelectorAll('.terminal').forEach(t => terminalObserver.observe(t));

/* ============================================
   COPY INSTALL COMMAND
   ============================================ */
function copyInstall() {
  navigator.clipboard.writeText('pip install prompt-drift').then(() => {
    const icon = document.getElementById('copy-icon');
    icon.outerHTML = `<svg id="copy-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`;

    const toast = document.getElementById('toast');
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        document.getElementById('copy-icon').outerHTML = `<svg id="copy-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>`;
      }, 300);
    }, 2000);
  });
}
window.copyInstall = copyInstall;

/* ============================================
   CARD MOUSE GLOW TRACKING
   ============================================ */
document.querySelectorAll('.problem-card, .feature-card').forEach(card => {
  card.addEventListener('mousemove', e => {
    const rect = card.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    const glow = card.querySelector('.card-glow');
    if (glow) {
      glow.style.background = `radial-gradient(circle at ${x}% ${y}%, rgba(124,106,247,0.12), transparent 60%)`;
    }
  });
});

/* ============================================
   HERO TEXT STAGGER
   ============================================ */
window.addEventListener('load', () => {
  const heroReveals = document.querySelectorAll('.hero .reveal');
  heroReveals.forEach((el, i) => {
    setTimeout(() => el.classList.add('visible'), 100 + i * 120);
  });
});
