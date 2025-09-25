function flipCard(id) {
  const card = document.getElementById(id);
  if (!card) return;
  card.classList.toggle('flipped');
  const pressed = card.classList.contains('flipped');
  card.setAttribute('aria-pressed', pressed ? 'true' : 'false');
  updateProgress();
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

// Delegação de eventos: garante flip em qualquer clique na área do card, mas ignora botões internos
document.addEventListener('click', function(e){
  const btnInside = e.target.closest('.icon-btn, a.btn, button');
  if(btnInside) return; // não vira quando for ação interna
  const card = e.target.closest && e.target.closest('.flip-card');
  if(card){ flipCard(card.id); }
});

// Favoritar / Difícil (client-side only por enquanto)
const favoriteSet = new Set();
const hardSet = new Set();

async function toggleFavorite(cardId, btn){
  const willActivate = !favoriteSet.has(cardId);
  btn.disabled = true; btn.classList.add('loading');
  try{
    const baralhoId = (document.querySelector('[data-baralho-id]')||{}).dataset?.baralhoId;
    const r = await fetch('/api/card/favorite', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ card_id: cardId, baralho_id: baralhoId, active: willActivate })});
    const j = await r.json();
    if(j && j.success){
      if(willActivate){ favoriteSet.add(cardId); btn.classList.add('active'); }
      else { favoriteSet.delete(cardId); btn.classList.remove('active'); }
    }
  } finally {
    btn.disabled = false; btn.classList.remove('loading');
  }
}

async function toggleHard(cardId, btn){
  const willActivate = !hardSet.has(cardId);
  btn.disabled = true; btn.classList.add('loading');
  try{
    const baralhoId = (document.querySelector('[data-baralho-id]')||{}).dataset?.baralhoId;
    const r = await fetch('/api/card/hard', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ card_id: cardId, baralho_id: baralhoId, active: willActivate })});
    const j = await r.json();
    if(j && j.success){
      if(willActivate){ hardSet.add(cardId); btn.classList.add('active'); }
      else { hardSet.delete(cardId); btn.classList.remove('active'); }
    }
  } finally {
    btn.disabled = false; btn.classList.remove('loading');
  }
}

// Progresso: número de cards virados
function updateProgress(){
  const totalEl = document.getElementById('progresso-total');
  const atualEl = document.getElementById('progresso-atual');
  if(!totalEl || !atualEl) return;
  const total = parseInt(totalEl.textContent || '0');
  const flipped = document.querySelectorAll('.flip-card.flipped').length;
  atualEl.textContent = Math.min(flipped, total);
  // progress bar (sequencial)
  const bar = document.getElementById('barra-progresso-fill');
  if(bar){
    const list = visibleCards();
    const idx = currentIndex();
    const pct = list.length ? Math.round(((idx+1) / list.length) * 100) : 0;
    bar.style.width = pct + '%';
  }
}

// Suporte a swipe (mobile) para flip
let touchStartX = 0, touchEndX = 0;
document.addEventListener('touchstart', function(e){
  const t = e.changedTouches[0];
  touchStartX = t.clientX;
});
document.addEventListener('touchend', function(e){
  const t = e.changedTouches[0];
  touchEndX = t.clientX;
  const dx = touchEndX - touchStartX;
  if(Math.abs(dx) > 50){
    // Encontra o card mais próximo do toque e faz flip
    const el = document.elementFromPoint(t.clientX, t.clientY);
    const card = el && el.closest ? el.closest('.flip-card') : null;
    if(card){ flipCard(card.id); }
  }
});

// --- Filtros (Todos / Favoritos / Difíceis) ---
function aplicarFiltro(tipo){
  const cards = document.querySelectorAll('.flip-card');
  let firstVisible = null;
  cards.forEach(c => {
    const isFav = c.getAttribute('data-is-fav') === '1' || c.querySelector('.icon-btn.fav')?.classList.contains('active');
    const isHard = c.getAttribute('data-is-hard') === '1' || c.querySelector('.icon-btn.hard')?.classList.contains('active');
    let visible = true;
    if(tipo === 'fav') visible = isFav;
    if(tipo === 'hard') visible = isHard;
    c.style.display = visible ? '' : 'none';
    if(visible && !firstVisible){ firstVisible = c; }
  });
  if(firstVisible){
    // foca no primeiro visível
    try { firstVisible.focus(); } catch(e){}
  }
  updateProgress();
}

// --- Navegação Passo-a-Passo ---
function visibleCards(){ return Array.from(document.querySelectorAll('.flip-card')).filter(c => c.style.display !== 'none'); }
function currentIndex(){
  const list = visibleCards();
  const active = document.activeElement && document.activeElement.closest ? document.activeElement.closest('.flip-card') : null;
  const idx = list.indexOf(active);
  return idx >= 0 ? idx : 0;
}
function navAnterior(){
  const list = visibleCards();
  if(list.length === 0) return;
  const idx = currentIndex();
  const prev = list[(idx - 1 + list.length) % list.length];
  prev.scrollIntoView({behavior:'smooth', block:'center'});
  try{ prev.focus(); } catch(e){}
  updateProgress();
}
function navProximo(){
  const list = visibleCards();
  if(list.length === 0) return;
  const idx = currentIndex();
  const next = list[(idx + 1) % list.length];
  next.scrollIntoView({behavior:'smooth', block:'center'});
  try{ next.focus(); } catch(e){}
  updateProgress();
}

// Modo Sequencial: mostra um card por vez
function toggleSequencial(on){
  const list = visibleCards();
  if(!on){
    // volta ao grid normal
    list.forEach(c => { c.style.visibility=''; });
    document.querySelector('.grid-cards').style.gridTemplateColumns='repeat(auto-fill, minmax(300px, 1fr))';
    updateProgress();
    return;
  }
  document.querySelector('.grid-cards').style.gridTemplateColumns='1fr';
  const idx = currentIndex();
  list.forEach((c,i)=>{ c.style.visibility = (i===idx) ? '' : 'hidden'; });
  updateProgress();
}

// Ao navegar no modo sequencial, atualiza visibilidade
const _oldNavPrev = navAnterior;
navAnterior = function(){
  const chk = document.getElementById('modo-sequencial');
  const on = chk && chk.checked;
  const list = visibleCards();
  const beforeIdx = currentIndex();
  _oldNavPrev();
  if(on){
    const afterIdx = currentIndex();
    list.forEach((c,i)=>{ c.style.visibility = (i===afterIdx) ? '' : 'hidden'; });
  }
};
const _oldNavNext = navProximo;
navProximo = function(){
  const chk = document.getElementById('modo-sequencial');
  const on = chk && chk.checked;
  const list = visibleCards();
  const beforeIdx = currentIndex();
  _oldNavNext();
  if(on){
    const afterIdx = currentIndex();
    list.forEach((c,i)=>{ c.style.visibility = (i===afterIdx) ? '' : 'hidden'; });
  }
};

// Toasts simples
function toast(msg, kind){
  const c = document.querySelector('.container');
  if(!c) return;
  const div = document.createElement('div');
  div.className = 'flash ' + (kind ? ('flash-' + kind) : '');
  div.textContent = msg;
  c.prepend(div);
  setTimeout(() => { div.style.opacity='0'; div.style.transform='translateY(-20px)'; setTimeout(()=>div.remove(), 300); }, 3000);
}

// Integração de toasts nos toggles
const _origToggleFavorite = toggleFavorite;
toggleFavorite = async function(cardId, btn){
  const before = btn.classList.contains('active');
  await _origToggleFavorite(cardId, btn);
  const after = btn.classList.contains('active');
  toast(after ? 'Adicionado aos favoritos' : 'Removido dos favoritos', 'info');
};
const _origToggleHard = toggleHard;
toggleHard = async function(cardId, btn){
  const before = btn.classList.contains('active');
  await _origToggleHard(cardId, btn);
  const after = btn.classList.contains('active');
  toast(after ? 'Marcado como difícil' : 'Desmarcado como difícil', 'warning');
};
