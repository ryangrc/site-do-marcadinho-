"""
Sistema de Controle de Fiado (Contas a Receber)
Gerencia dívidas dos clientes e recebimentos
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models.database import query_db, get_db_connection
from datetime import datetime

fiado_bp = Blueprint('fiado', __name__)

@fiado_bp.route('/')
def index():
    """Página principal de controle de fiado"""
    # Data atual para marcar contas atrasadas
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    # Lista clientes com dívidas pendentes
    clientes_devedores = query_db("""
        SELECT c.id, c.nome, c.telefone, c.saldo_devedor,
               COUNT(cr.id) as total_contas,
               SUM(CASE WHEN cr.status = 'pendente' THEN cr.valor ELSE 0 END) as total_pendente
        FROM clientes c
        LEFT JOIN contas_receber cr ON c.id = cr.cliente_id
        WHERE c.saldo_devedor > 0 OR cr.status = 'pendente'
        GROUP BY c.id
        ORDER BY total_pendente DESC
    """)
    
    # Lista todas as contas pendentes com detalhes
    contas_pendentes = query_db("""
        SELECT cr.*, c.nome as cliente_nome, v.data as data_venda
        FROM contas_receber cr
        JOIN clientes c ON cr.cliente_id = c.id
        LEFT JOIN vendas v ON cr.venda_id = v.id
        WHERE cr.status = 'pendente'
        ORDER BY cr.data_vencimento
    """)
    
    return render_template('fiado.html', 
                         clientes=clientes_devedores, 
                         contas=contas_pendentes,
                         hoje=hoje)

@fiado_bp.route('/cliente/<int:cliente_id>')
def detalhes_cliente(cliente_id):
    """Mostra detalhes das dívidas de um cliente específico"""
    cliente = query_db(
        "SELECT * FROM clientes WHERE id = ?", 
        (cliente_id,), one=True
    )
    
    contas = query_db("""
        SELECT cr.*, v.data as data_venda
        FROM contas_receber cr
        LEFT JOIN vendas v ON cr.venda_id = v.id
        WHERE cr.cliente_id = ?
        ORDER BY cr.data_vencimento DESC
    """, (cliente_id,))
    
    return render_template('fiado_cliente.html', 
                         cliente=dict(cliente), 
                         contas=[dict(c) for c in contas])

@fiado_bp.route('/registrar-pagamento', methods=['POST'])
def registrar_pagamento():
    """Registra o pagamento de uma dívida"""
    data = request.get_json()
    conta_id = data.get('conta_id')
    valor_pago = float(data.get('valor_pago', 0))
    
    conn = get_db_connection()
    try:
        # Busca informações da conta
        conta = conn.execute(
            "SELECT * FROM contas_receber WHERE id = ?", 
            (conta_id,)
        ).fetchone()
        
        if not conta:
            return jsonify({'success': False, 'error': 'Conta não encontrada'})
        
        cliente_id = conta['cliente_id']
        valor_conta = conta['valor']
        
        # Atualiza status da conta
        if valor_pago >= valor_conta:
            # Quitação total
            conn.execute(
                """UPDATE contas_receber 
                   SET status = 'pago', 
                       data_pagamento = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (conta_id,)
            )
        else:
            # Pagamento parcial - cria nova conta com o restante
            novo_valor = valor_conta - valor_pago
            conn.execute(
                """UPDATE contas_receber 
                   SET valor = ?,
                       status = CASE WHEN ? >= valor THEN 'pago' ELSE 'pendente' END
                   WHERE id = ?""",
                (novo_valor, valor_pago, conta_id)
            )
        
        # Atualiza saldo devedor do cliente
        conn.execute(
            "UPDATE clientes SET saldo_devedor = MAX(0, saldo_devedor - ?) WHERE id = ?",
            (valor_pago, cliente_id)
        )
        
        conn.commit()
        return jsonify({
            'success': True,
            'mensagem': f'Pagamento de R$ {valor_pago:.2f} registrado com sucesso!'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@fiado_bp.route('/api/contas-cliente/<int:cliente_id>')
def api_contas_cliente(cliente_id):
    """API para buscar contas pendentes de um cliente"""
    contas = query_db("""
        SELECT id, valor, data_vencimento, status
        FROM contas_receber
        WHERE cliente_id = ? AND status = 'pendente'
        ORDER BY data_vencimento
    """, (cliente_id,))
    return jsonify([dict(c) for c in contas])