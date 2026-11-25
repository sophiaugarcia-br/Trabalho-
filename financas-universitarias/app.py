from flask import Flask 

import database
from financas.rotas import painel, lancamentos, metas

app = Flask(__name__)

database.inicializar_banco()

def formatar_brl(centavos):
    texto = f"{centavos / 100:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")

app.add_template_filter(formatar_brl, "brl")

app.register_blueprint(metas.bp)
app.register_blueprint(painel.bp)
app.register_blueprint(lancamentos.bp)

if __name__ == "__main__":
    app.run(debug=True)