from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for

from financas.rotas import _mocks as meta_service

bp = Blueprint("metas", __name__, url_prefix="/metas")

@bp.route("/", methods=["GET", "POST"])
def listar():
    erros = []
    if request.method == "POST":
        erros = meta_service.cadastrar_meta(request.form.to_dict())
        if not erros:
            return redirect(url_for("metas.listar"))

    dados = meta_service.painel_metas(date.today())
    return render_template("metas.html", itens=dados["itens"], viab=dados["viabilidade"], erros=erros)

@bp.route("/<int:meta_id>/aporte", methods=["POST"])
def aporte(meta_id):
    meta_service.registrar_aporte(meta_id, request.form["valor"])
    return redirect(url_for("metas.listar"))

@bp.route("/<int:meta_id>/concluir", methods=["POST"])
def concluir(meta_id):
    meta_service.concluir(meta_id)
    return redirect(url_for("metas.listar"))