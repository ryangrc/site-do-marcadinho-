"""
Rotas para gerenciamento de produtos
CRUD completo: Create, Read, Update, Delete
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models.database import query_db, get_db_connection

# Cria o Blueprint para produtos
produtos_bp = Blueprint('produtos', __name__)

@produtos_bp.route('/')
def listar():
    """Lista todos os produtos cadastrados"""
    produtos = query_db("SELECT * FROM produtos ORDER BY nome")
    return render_template('produtos.html', produtos=produtos)

@produtos_bp.route('/api/listar')
def api_listar():
    """API para listar produtos (usado em AJAX)"""
    produtos = query_db("SELECT * FROM produtos ORDER BY nome")
    return jsonify([dict(row) for row in produtos])

@produtos_bp.route('/adicionar', methods=['POST'])
def adicionar():
    """Adiciona um novo produto"""
    nome = request.form.get('nome')
    preco = float(request.form.get('preco', 0))
    quantidade = int(request.form.get('quantidade', 0))
    
    query_db(
        "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
        (nome, preco, quantidade)
    )
    
    return redirect(url_for('produtos.listar'))

@produtos_bp.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    """Edita um produto existente"""
    nome = request.form.get('nome')
    preco = float(request.form.get('preco', 0))
    quantidade = int(request.form.get('quantidade', 0))
    
    query_db(
        "UPDATE produtos SET nome=?, preco=?, quantidade=? WHERE id=?",
        (nome, preco, quantidade, id)
    )
    
    return redirect(url_for('produtos.listar'))

@produtos_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    """Exclui um produto"""
    try:
        query_db("DELETE FROM produtos WHERE id=?", (id,))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})