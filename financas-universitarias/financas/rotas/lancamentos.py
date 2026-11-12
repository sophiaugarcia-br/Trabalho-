from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
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