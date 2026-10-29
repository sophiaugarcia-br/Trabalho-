from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for

import database

app = Flask(__name__)

database.inicializar_banco()


@app.route("/")
def home():
    resumo = database.resumo_mes_atual()
    transacoes = database.listar_transacoes()
    categorias = database.listar_categorias()
    despesas_cat = database.despesas_por_categoria_mes_atual()

    chart_labels = [d["categoria"] for d in despesas_cat]
    chart_values = [d["total"] for d in despesas_cat]

    return render_template(
        "index.html",
        resumo=resumo,
        transacoes=transacoes,
        categorias=categorias,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )


@app.route("/add", methods=["POST"])
def add_transaction():
    categoria_id = int(request.form["categoria_id"])
    descricao = request.form["descricao"]
    valor = float(request.form["valor"])
    data_str = request.form["data"]
    data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
    tipo = request.form["tipo"]

    database.inserir_transacao(
        categoria_id=categoria_id,
        descricao=descricao,
        valor=valor,
        data=data_obj,
        tipo=tipo,
    )

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)