"""
Rotas para gerenciamento de clientes
Inclui controle de saldo devedor
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models.database import query_db

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/')
def listar():
    """Lista todos os clientes com seus saldos"""
    clientes = query_db("""
        SELECT c.*, 
               COALESCE(SUM(cr.valor), 0) as total_devido,
               COUNT(CASE WHEN cr.status = 'pendente' THEN 1 END) as contas_pendentes
        FROM clientes c
        LEFT JOIN contas_receber cr ON c.id = cr.cliente_id
        GROUP BY c.id
        ORDER BY c.nome
    """)
    return render_template('clientes.html', clientes=clientes)

@clientes_bp.route('/adicionar', methods=['POST'])
def adicionar():
    """Cadastra um novo cliente"""
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')
    
    query_db(
        "INSERT INTO clientes (nome, telefone, saldo_devedor) VALUES (?, ?, 0)",
        (nome, telefone)
    )
    
    return redirect(url_for('clientes.listar'))

@clientes_bp.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    """Edita dados do cliente"""
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')
    
    query_db(
        "UPDATE clientes SET nome=?, telefone=? WHERE id=?",
        (nome, telefone, id)
    )
    
    return redirect(url_for('clientes.listar'))

@clientes_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    """Remove um cliente do sistema"""
    try:
        query_db("DELETE FROM clientes WHERE id=?", (id,))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@clientes_bp.route('/api/buscar')
def api_buscar():
    """API para buscar clientes (usado no select de vendas)"""
    termo = request.args.get('q', '')
    clientes = query_db(
        "SELECT id, nome, telefone, saldo_devedor FROM clientes WHERE nome LIKE ? ORDER BY nome",
        (f'%{termo}%',)
    )
    return jsonify([dict(row) for row in clientes])