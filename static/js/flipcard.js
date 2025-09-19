function flipCard(id) {
  const card = document.getElementById(id);
  if (card) {
    card.classList.toggle('flipped');
  }
}
