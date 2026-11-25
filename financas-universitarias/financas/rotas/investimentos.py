from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for

from financas.rotas import _mocks_investimentos as investimento_service   # depois: from financas.servicos import investimento_service

bp = Blueprint("investimentos", __name__, url_prefix="/investimentos")


def _ler_mes(texto, hoje):
    """'2026-11' -> (2026, 11). Sem parâmetro ou inválido, usa o mês corrente."""
    try:
        ano, mes = texto.split("-")
        ano, mes = int(ano), int(mes)
        if 1 <= mes <= 12:
            return ano, mes
    except (AttributeError, ValueError):
        pass
    return hoje.year, hoje.month


@bp.route("/", methods=["GET", "POST"])
def listar():
    erros = []
    if request.method == "POST":
        erros = investimento_service.cadastrar_investimento(request.form.to_dict())
        if not erros:
            return redirect(url_for("investimentos.listar"))

    ano, mes = _ler_mes(request.args.get("mes"), date.today())
    return render_template(
        "investimentos.html",
        resumo=investimento_service.resumo_mes(ano, mes),
        mes_atual=f"{ano}-{mes:02d}",
        erros=erros,
    )