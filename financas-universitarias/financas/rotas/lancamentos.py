from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort

import database

bp = Blueprint("lancamentos", __name__, url_prefix="/lancamentos")


@bp.route("/", methods=["GET", "POST"])
def listar():
    if request.method == "POST":
        database.inserir_transacao(
            categoria_id=int(request.form["categoria_id"]),
            descricao=request.form["descricao"],
            valor=float(request.form["valor"]),
            data=datetime.strptime(request.form["data"], "%Y-%m-%d").date(),
            tipo=request.form["tipo"],
        )
        return redirect(url_for("lancamentos.listar"))

    return render_template(
        "lancamentos.html",
        transacoes=database.listar_transacoes(),
        categorias=database.listar_categorias(),
    )


@bp.route("/<int:transacao_id>/editar", methods=["GET", "POST"])
def editar(transacao_id):
    if request.method == "POST":
        database.atualizar_transacao(
            transacao_id,
            categoria_id=int(request.form["categoria_id"]),
            descricao=request.form["descricao"],
            valor=float(request.form["valor"]),
            data=datetime.strptime(request.form["data"], "%Y-%m-%d").date(),
            tipo=request.form["tipo"],
        )
        return redirect(url_for("lancamentos.listar"))

    t = database.buscar_transacao(transacao_id)
    if t is None:
        abort(404)
    return render_template(
        "editar_lancamento.html",
        t=t,
        categorias=database.listar_categorias(),
    )


@bp.route("/<int:transacao_id>/excluir", methods=["POST"])
def excluir(transacao_id):
    database.deletar_transacao(transacao_id)
    return redirect(url_for("lancamentos.listar"))

