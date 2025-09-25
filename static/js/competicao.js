// Seleção de chips de amigos (apenas um)
document.addEventListener('DOMContentLoaded', function() {
  const chipsAmigos = document.querySelectorAll('.chip-amigo');
  const inputAmigo = document.getElementById('amigo');
  chipsAmigos.forEach(chip => {
    chip.addEventListener('click', function() {
      chipsAmigos.forEach(c => c.classList.remove('selected'));
      chip.classList.add('selected');
      inputAmigo.value = chip.dataset.id;
    });
  });
});
// Seleção de chips de baralhos
document.addEventListener('DOMContentLoaded', function() {
  const chips = document.querySelectorAll('.chip-baralho');
  const inputDecks = document.getElementById('decks');
  chips.forEach(chip => {
    chip.addEventListener('click', function() {
      chip.classList.toggle('selected');
      // Atualiza campo hidden
      const selecionados = Array.from(document.querySelectorAll('.chip-baralho.selected')).map(c => c.dataset.id);
      inputDecks.value = JSON.stringify(selecionados);
    });
  });
});
// Preenche selects com nomes reais vindos do backend
function preencherSelects(amigos, baralhos) {
  const amigoSelect = document.getElementById('amigo');
  amigoSelect.innerHTML = '';
  if (amigos.length === 0) {
    amigoSelect.innerHTML = '<option disabled>Nenhum amigo encontrado</option>';
  } else {
    amigos.forEach(a => {
      amigoSelect.innerHTML += `<option value="${a.id}">${a.nome}</option>`;
    });
  }
  const deckSelect = document.getElementById('deck');
  deckSelect.innerHTML = '';
  if (baralhos.length === 0) {
    deckSelect.innerHTML = '<option disabled>Nenhum baralho encontrado</option>';
  } else {
    baralhos.forEach(b => {
      deckSelect.innerHTML += `<option value="${b.id}">${b.nome}</option>`;
    });
  }
}

// Recebe dados do backend via variável global (inserida no template)
window.onload = function() {
  if (window.amigos && window.baralhos) {
    preencherSelects(window.amigos, window.baralhos);
  }
  atualizarDesafios();
};
// Atualiza lista de desafios pendentes na página principal
function atualizarDesafios() {
  fetch('/competicao/desafios')
    .then(res => res.json())
    .then(data => {
      const ul = document.getElementById('desafios-list');
      ul.innerHTML = '';
      if (data.desafios.length === 0) {
        ul.innerHTML = '<li style="text-align:center;color:#888;">Nenhum desafio pendente</li>';
      } else {
        data.desafios.forEach(d => {
          ul.innerHTML += `<li><strong>${d.de}</strong> desafiou você no baralho <strong>${d.baralho}</strong>
            <button onclick="aceitarDesafio('${d.id}')" class="btn-enviar btn-success">Aceitar</button>
            <button onclick="recusarDesafio('${d.id}')" class="btn-enviar btn-danger">Recusar</button>
          </li>`;
        });
      }
    });
}

window.onload = atualizarDesafios;
function abrirDesafio() {
  document.getElementById('desafio-form').style.display = 'block';
}
function fecharDesafio() {
  document.getElementById('desafio-form').style.display = 'none';
}
function abrirRanking() {
  document.getElementById('ranking').style.display = 'block';
  fetch('/competicao/ranking')
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('ranking-list');
      list.innerHTML = '';
      data.ranking.forEach((item, idx) => {
        list.innerHTML += `<li><strong>${idx+1}º</strong> ${item.nome} - ${item.pontos} pts</li>`;
      });
    });
}
function fecharRanking() {
  document.getElementById('ranking').style.display = 'none';
}
document.getElementById('formDesafio').onsubmit = function(e) {
  e.preventDefault();
  const amigo = document.getElementById('amigo').value;
  const decks = JSON.parse(document.getElementById('decks').value || '[]');
  if (!amigo) {
    mostrarMensagem('Selecione um amigo!', 'danger');
    return;
  }
  if (decks.length === 0) {
    mostrarMensagem('Selecione pelo menos um baralho!', 'danger');
    return;
  }
  fetch('/competicao/convidar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user1: window.usuario.id, user2: amigo, deck_ids: decks })
  })
  .then(res => res.json())
  .then(data => {
    mostrarMensagem(data.msg || 'Desafio enviado!', 'success');
    fecharDesafio();
    atualizarDesafios();
  })
  .catch(() => {
    mostrarMensagem('Erro ao enviar desafio.', 'danger');
  });
}

function mostrarMensagem(msg, tipo) {
  const div = document.createElement('div');
  div.className = 'flash flash-' + tipo;
  div.innerText = msg;
  document.querySelector('.competicao-container').prepend(div);
  setTimeout(() => div.remove(), 3000);
}

function aceitarDesafio(id) {
  fetch('/competicao/aceitar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ comp_id: id })
  }).then(r => r.json()).then(data => {
    mostrarMensagem(data.msg || 'Competição aceita!', 'success');
    atualizarDesafios();
  }).catch(() => mostrarMensagem('Erro ao aceitar.', 'danger'));
}

function recusarDesafio(id) {
  fetch('/competicao/recusar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ comp_id: id })
  }).then(r => r.json()).then(data => {
    mostrarMensagem(data.msg || 'Desafio recusado!', 'info');
    atualizarDesafios();
  }).catch(() => mostrarMensagem('Erro ao recusar.', 'danger'));
}