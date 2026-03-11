/**
 * Mercadinho Conectado - JavaScript Principal
 * Funcionalidades globais e utilitários
 */

// Sistema de Notificações Toast
function mostrarToast(mensagem, tipo = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;
    toast.textContent = mensagem;
    
    container.appendChild(toast);
    
    // Remove após 3 segundos
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Função de Sincronização Simulada
function sincronizarNuvem() {
    const btn = document.getElementById('btn-sync');
    const originalText = btn.innerHTML;
    
    // Desabilita botão durante sincronização
    btn.disabled = true;
    btn.innerHTML = '<span class="icon">⏳</span><span>Sincronizando...</span>';
    
    // Simula processo de sincronização
    setTimeout(() => {
        btn.innerHTML = '<span class="icon">✅</span><span>Sincronizado!</span>';
        btn.style.background = '#4CAF50';
        
        mostrarToast('Dados sincronizados com sucesso! (Modo Demo)', 'success');
        
        // Restaura botão após 2 segundos
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = originalText;
            btn.style.background = '';
        }, 2000);
    }, 1500);
}

// Confirmação antes de sair da página com dados não salvos
let formAlterado = false;

document.addEventListener('DOMContentLoaded', function() {
    // Monitora formulários para aviso de saída
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('change', () => formAlterado = true);
        form.addEventListener('submit', () => formAlterado = false);
    });
});

window.addEventListener('beforeunload', function(e) {
    if (formAlterado) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Atalhos de teclado úteis
document.addEventListener('keydown', function(e) {
    // ESC fecha modais abertos
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }
    
    // F1 abre ajuda (pode ser implementado)
    if (e.key === 'F1') {
        e.preventDefault();
        mostrarToast('Ajuda: Use ESC para fechar janelas', 'info');
    }
});

// Registra Service Worker para funcionamento offline (PWA básico)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Em produção, registrar um service worker real
        console.log('Mercadinho Conectado pronto para uso offline');
    });
}

// Funções utilitárias globais
const Utils = {
    // Formata valor para moeda brasileira
    formatarMoeda: function(valor) {
        return 'R$ ' + parseFloat(valor).toFixed(2).replace('.', ',');
    },
    
    // Formata data para padrão brasileiro
    formatarData: function(dataString) {
        const data = new Date(dataString);
        return data.toLocaleDateString('pt-BR');
    },
    
    // Valida CPF (básico)
    validarCPF: function(cpf) {
        return cpf.length === 11; // Simplificado para demo
    },
    
    // Gera ID único local
    gerarId: function() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
};