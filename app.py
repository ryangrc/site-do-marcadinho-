"""
Mercadinho Conectado - Sistema de Gestão para Pequenos Comércios Rurais
Arquivo principal que inicializa a aplicação Flask e registra as rotas
"""

from flask import Flask, render_template
from models.database import init_db
from routes.produtos import produtos_bp
from routes.clientes import clientes_bp
from routes.vendas import vendas_bp
from routes.fiado import fiado_bp

# Cria a aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mercadinho-conectado-2024'  # Chave para sessões

# Inicializa o banco de dados SQLite
init_db()

# Registra os Blueprints (módulos de rotas)
app.register_blueprint(produtos_bp, url_prefix='/produtos')
app.register_blueprint(clientes_bp, url_prefix='/clientes')
app.register_blueprint(vendas_bp, url_prefix='/vendas')
app.register_blueprint(fiado_bp, url_prefix='/fiado')

@app.route('/')
def index():
    """Página inicial do sistema"""
    return render_template('index.html')

@app.route('/relatorios')
def relatorios():
    """Página de relatórios"""
    return render_template('relatorios.html')

if __name__ == '__main__':
    # Executa o servidor em modo debug (desenvolvimento)
    app.run(debug=True, host='0.0.0.0', port=5000)