"""
Sistema de Ponto de Venda (PDV)
Processa vendas à vista e atualiza estoque automaticamente
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models.database import query_db, get_db_connection
from datetime import datetime

vendas_bp = Blueprint('vendas', __name__)

@vendas_bp.route('/')
def pdv():
    """Interface do PDV - carrega produtos disponíveis"""
    produtos = query_db("SELECT * FROM produtos WHERE quantidade > 0 ORDER BY nome")
    return render_template('vendas.html', produtos=produtos)

@vendas_bp.route('/registrar', methods=['POST'])
def registrar():
    """
    Registra uma nova venda
    Atualiza estoque e cria conta a receber se for fiado
    """
    data = request.get_json()
    itens = data.get('itens', [])  # Lista de {produto_id, quantidade, preco_unitario}
    tipo_pagamento = data.get('tipo_pagamento', 'dinheiro')
    cliente_id = data.get('cliente_id')  # Opcional, apenas para fiado
    valor_total = data.get('valor_total', 0)
    
    conn = get_db_connection()
    try:
        # 1. Cria a venda
        cursor = conn.execute(
            """INSERT INTO vendas (valor_total, tipo_pagamento, cliente_id) 
               VALUES (?, ?, ?)""",
            (valor_total, tipo_pagamento, cliente_id)
        )
        venda_id = cursor.lastrowid
        
        # 2. Processa cada item da venda
        for item in itens:
            produto_id = item['produto_id']
            quantidade = item['quantidade']
            preco_unitario = item['preco_unitario']
            
            # Insere item da venda
            conn.execute(
                """INSERT INTO venda_itens (venda_id, produto_id, quantidade, preco_unitario)
                   VALUES (?, ?, ?, ?)""",
                (venda_id, produto_id, quantidade, preco_unitario)
            )
            
            # Atualiza estoque do produto
            conn.execute(
                "UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?",
                (quantidade, produto_id)
            )
        
        # 3. Se for fiado, cria conta a receber
        if tipo_pagamento == 'fiado' and cliente_id:
            # Define data de vencimento para 30 dias
            data_vencimento = datetime.now().strftime('%Y-%m-%d')
            
            conn.execute(
                """INSERT INTO contas_receber 
                   (cliente_id, venda_id, valor, data_vencimento, status)
                   VALUES (?, ?, ?, date('now', '+30 days'), 'pendente')""",
                (cliente_id, venda_id, valor_total)
            )
            
            # Atualiza saldo devedor do cliente
            conn.execute(
                "UPDATE clientes SET saldo_devedor = saldo_devedor + ? WHERE id = ?",
                (valor_total, cliente_id)
            )
        
        conn.commit()
        return jsonify({
            'success': True, 
            'venda_id': venda_id,
            'mensagem': 'Venda registrada com sucesso!'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@vendas_bp.route('/historico')
def historico():
    """Mostra histórico de vendas"""
    vendas = query_db("""
        SELECT v.*, c.nome as cliente_nome,
               COUNT(vi.id) as total_itens
        FROM vendas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        LEFT JOIN venda_itens vi ON v.id = vi.venda_id
        GROUP BY v.id
        ORDER BY v.data DESC
        LIMIT 50
    """)
    return render_template('relatorios.html', vendas=vendas)