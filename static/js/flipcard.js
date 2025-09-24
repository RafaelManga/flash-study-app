function flipCard(id) {
  const card = document.getElementById(id);
  if (card) {
    card.classList.toggle('flipped');
    try {
      const pressed = card.classList.contains('flipped');
      card.setAttribute('aria-pressed', pressed ? 'true' : 'false');
    } catch (e) {}
  }
}

// Acessibilidade: permite flip via teclado (Enter/Espaço)
document.addEventListener('keydown', function(e) {
  const target = e.target;
  if (!target || !target.classList) return;
  const isFlipCard = target.classList.contains('flip-card');
  if (!isFlipCard) return;
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    flipCard(target.id);
  }
});
