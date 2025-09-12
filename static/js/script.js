// --- Permissões colaborativas AJAX ---
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.form-permissoes-membro').forEach(form => {
        // UX: mostrar botão salvar só se alterar
        const select = form.querySelector('select[name="rank"]');
        const btn = form.querySelector('button[type="submit"]');
        let original = select.value;
        btn.style.display = 'none';
        // Selo dinâmico de rank (corrigido para cada membro)
        // Busca o badge apenas dentro do bloco do membro
        const badge = form.closest('div[style*="background"]')?.querySelector('.badge-rank');
        function updateBadge() {
            if (!badge) return;
            if (select.value === 'colider') {
                badge.textContent = 'Colíder';
                badge.setAttribute('data-rank', 'colider');
                badge.style.backgroundColor = '#2563eb';
            } else {
                badge.textContent = 'Visitante';
                badge.setAttribute('data-rank', 'visitante');
                badge.style.backgroundColor = '#64748b';
            }
        }
        updateBadge();
        select.addEventListener('change', function() {
            if (select.value !== original) {
                btn.style.display = '';
            } else {
                btn.style.display = 'none';
            }
            updateBadge();
        });
        // Após salvar, sincronizar valor original e selo
        form.addEventListener('submit', function() {
            setTimeout(() => {
                original = select.value;
                updateBadge();
            }, 200);
        });
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const baralhoId = form.getAttribute('data-baralho-id');
            const memberId = form.getAttribute('data-member-id');
            const btn = form.querySelector('button[type="submit"]');
            const feedback = form.querySelector('.permissao-feedback');
            const rank = form.querySelector('select[name="rank"]').value;
            btn.disabled = true;
            btn.textContent = 'Salvando...';
            feedback.textContent = '';
            fetch(`/api/baralho/${baralhoId}/permissoes/${memberId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rank })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    feedback.innerHTML = '<span style="color:var(--success);font-weight:600;">&#10003; Salvo!</span>';
                } else {
                    feedback.innerHTML = '<span style="color:#dc2626;font-weight:600;">Erro</span>';
                    alert(data.error || 'Erro ao salvar permissões.');
                }
                btn.textContent = 'Salvar';
                btn.disabled = false;
                btn.style.display = 'none';
                setTimeout(() => { feedback.textContent = ''; }, 1800);
            })
            .catch(() => {
                feedback.innerHTML = '<span style="color:#dc2626;font-weight:600;">Erro</span>';
                btn.textContent = 'Salvar';
                btn.disabled = false;
                btn.style.display = 'none';
                setTimeout(() => { feedback.textContent = ''; }, 1800);
            });
        });
    });
});
// static/js/script.js

// Função para alternar tema
function alternarTema() {
    fetch('/alternar_tema', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        document.documentElement.setAttribute('data-theme', data.tema);
        atualizarIconeTema(data.tema);
    })
    .catch(error => {
        console.error('Erro ao alternar tema:', error);
    });
}

// Atualiza o ícone do botão de tema
function atualizarIconeTema(tema) {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = tema === 'dark' ? '☀️' : '🌙';
    }
}

// Inicializa o tema ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    atualizarIconeTema(currentTheme);

    // Função para virar cards ao clicar
    const flipCards = document.querySelectorAll('.flip-card');

    flipCards.forEach(card => {
        card.addEventListener('click', function() {
            this.classList.toggle('flipped');
        });
    });

    // Auto-refresh para countdown da IA
    const tempoRestante = document.getElementById('tempo-restante');
    if (tempoRestante) {
        const segundos = parseInt(tempoRestante.textContent);
        if (segundos > 0) {
            let contador = segundos;
            const interval = setInterval(() => {
                contador--;
                if (contador <= 0) {
                    clearInterval(interval);
                    location.reload(); // Recarrega a página quando o cooldown termina
                } else {
                    const minutos = Math.floor(contador / 60);
                    const segs = contador % 60;
                    tempoRestante.textContent = `${minutos}m ${segs}s`;
                }
            }, 1000);
        }
    }

    // Timer do desafio
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        let tempoRestante = parseInt(timerElement.dataset.tempo);

        const interval = setInterval(() => {
            tempoRestante--;
            timerElement.textContent = `⏰ ${tempoRestante}s`;

            if (tempoRestante <= 10) {
                timerElement.style.background = 'var(--danger)';
                timerElement.style.animation = 'pulse 0.5s infinite';
            }

            if (tempoRestante <= 0) {
                clearInterval(interval);
                // Auto-submit do formulário quando o tempo acaba
                document.getElementById('form-resposta').submit();
            }
        }, 1000);
    }
});

// Função para confirmar exclusões
function confirmarExclusao(mensagem) {
    return confirm(mensagem || 'Tem certeza que deseja excluir? Esta ação não pode ser desfeita.');
}

// Função para copiar texto para clipboard
function copiarTexto(texto, event) {
    if (event) event.preventDefault();

    navigator.clipboard.writeText(texto).then(() => {
        // Feedback visual
        const btn = event ? event.target : null;
        if (btn) {
            const textoOriginal = btn.textContent;
            btn.textContent = 'Copiado!';
            btn.style.background = 'var(--success)';

            setTimeout(() => {
                btn.textContent = textoOriginal;
                btn.style.background = '';
            }, 2000);
        } else {
            // Feedback alternativo se não houver botão
            alert('ID copiado para a área de transferência!');
        }
    }).catch(err => {
        console.error('Erro ao copiar:', err);
        alert('Erro ao copiar. Tente selecionar o texto manualmente.');
    });
}

// Função para preview de upload de imagem
function previewImagem(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('avatar-preview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Validação de formulários em tempo real
document.addEventListener('DOMContentLoaded', function() {
    // Validação de senha
    const senhaInput = document.getElementById('senha');
    if (senhaInput) {
        senhaInput.addEventListener('input', function() {
            const senha = this.value;
            const feedback = document.getElementById('senha-feedback');

            if (feedback) {
                if (senha.length < 6) {
                    feedback.textContent = 'A senha deve ter pelo menos 6 caracteres';
                    feedback.style.color = 'var(--danger)';
                } else {
                    feedback.textContent = 'Senha válida';
                    feedback.style.color = 'var(--success)';
                }
            }
        });
    }

    // Validação de email
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('input', function() {
            const email = this.value;
            const feedback = document.getElementById('email-feedback');
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (feedback) {
                if (!emailRegex.test(email) && email.length > 0) {
                    feedback.textContent = 'Email inválido';
                    feedback.style.color = 'var(--danger)';
                } else if (email.length > 0) {
                    feedback.textContent = 'Email válido';
                    feedback.style.color = 'var(--success)';
                } else {
                    feedback.textContent = '';
                }
            }
        });
    }
});