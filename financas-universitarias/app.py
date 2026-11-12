from flask import Flask

import database
from financas.rotas import painel, lancamentos

app = Flask(__name__)

database.inicializar_banco()

app.register_blueprint(painel.bp)
app.register_blueprint(lancamentos.bp)

if __name__ == "__main__":
    app.run(debug=True)