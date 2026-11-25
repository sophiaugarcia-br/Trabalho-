from flask import Blueprint, abort, render_template, send_file

from financas.servicos import relatorio_service

bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")


def _ler_ym(texto):
    """'2026-11' -> (2026, 11). Inválido dá 404."""
    try:
        ano, mes = texto.split("-")
        ano, mes = int(ano), int(mes)
        if 1 <= mes <= 12:
            return ano, mes
    except ValueError:
        pass
    abort(404)


@bp.route("/")
def listar():
    meses = [{"ym": f"{a}-{m:02d}",
              "nome": f"{relatorio_service.MESES[m - 1].capitalize()} de {a}"}
             for a, m in relatorio_service.meses_disponiveis()]
    return render_template("relatorios.html", meses=meses)


@bp.route("/<ym>")
def ver(ym):
    ano, mes = _ler_ym(ym)
    rel = relatorio_service.montar_relatorio(ano, mes)
    nome = f"{relatorio_service.MESES[mes - 1].capitalize()} de {ano}"
    return render_template("relatorio.html", rel=rel, ym=ym, nome_mes=nome)


@bp.route("/<ym>/pdf")
def baixar_pdf(ym):
    ano, mes = _ler_ym(ym)
    caminho = relatorio_service.garantir_pdf(ano, mes)
    return send_file(caminho, as_attachment=True, download_name=f"relatorio-{ym}.pdf")