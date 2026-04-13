const toggleBtn = document.getElementById('theme-toggle');
const body = document.body;

// Check system preference
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
if (prefersDark) body.setAttribute('data-theme', 'dark');

toggleBtn.addEventListener('click', () => {
    const isDark = body.getAttribute('data-theme') === 'dark';
    if (isDark) {
        body.removeAttribute('data-theme');
        toggleBtn.textContent = '🌙';
    } else {
        body.setAttribute('data-theme', 'dark');
        toggleBtn.textContent = '☀️';
    }
});