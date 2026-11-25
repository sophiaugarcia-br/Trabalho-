from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, abort, flash

import database

bp = Blueprint("lancamentos", __name__, url_prefix="/lancamentos")


def _ler_form(form):
    """Valida o formulário. Devolve (dados, erros)."""
    erros = []

    descricao = form.get("descricao", "").strip()
    if not descricao:
        erros.append("Informe a descrição.")

    valor = 0
    try:
        valor = float(form.get("valor", "").replace(",", "."))
        if valor <= 0:
            erros.append("O valor deve ser maior que zero.")
    except ValueError:
        erros.append("Valor inválido.")

    data = None
    try:
        data = datetime.strptime(form.get("data", ""), "%Y-%m-%d").date()
    except ValueError:
        erros.append("Data inválida.")

    tipo = form.get("tipo")
    if tipo not in ("Receita", "Despesa"):
        erros.append("Escolha o tipo.")

    categoria_id = None
    try:
        categoria_id = int(form.get("categoria_id", ""))
    except ValueError:
        erros.append("Escolha a categoria.")

    dados = {"categoria_id": categoria_id, "descricao": descricao,
             "valor": valor, "data": data, "tipo": tipo}
    return dados, erros


def _ler_mes(texto):
    """'2026-11' -> (2026, 11). Vazio ou inválido -> (None, None)."""
    try:
        ano, mes = int(texto[:4]), int(texto[5:7])
        if 1 <= mes <= 12:
            return ano, mes
    except ValueError:
        pass
    return None, None


@bp.route("/", methods=["GET", "POST"])
def listar():
    if request.method == "POST":
        dados, erros = _ler_form(request.form)
        if erros:
            for e in erros:
                flash(e, "erro")
        else:
            database.inserir_transacao(**dados)
            flash("Transação salva!", "ok")
        return redirect(url_for("lancamentos.listar"))

    tipo = request.args.get("tipo")
    if tipo not in ("Receita", "Despesa"):
        tipo = None
    categoria = request.args.get("categoria", type=int)
    mes_texto = request.args.get("mes", "")
    ano, mes = _ler_mes(mes_texto)

    transacoes = database.listar_transacoes(mes=mes, ano=ano, tipo=tipo, categoria_id=categoria)
    filtros = {"tipo": tipo, "categoria": categoria, "mes": mes_texto if mes else ""}

    return render_template("lancamentos.html", transacoes=transacoes,
                           categorias=database.listar_categorias(), filtros=filtros)


@bp.route("/<int:transacao_id>/editar", methods=["GET", "POST"])
def editar(transacao_id):
    if request.method == "POST":
        dados, erros = _ler_form(request.form)
        if erros:
            for e in erros:
                flash(e, "erro")
            return redirect(url_for("lancamentos.editar", transacao_id=transacao_id))
        database.atualizar_transacao(transacao_id, **dados)
        flash("Transação atualizada!", "ok")
        return redirect(url_for("lancamentos.listar"))

    t = database.buscar_transacao(transacao_id)
    if t is None:
        abort(404)
    return render_template("editar_lancamento.html", t=t,
                           categorias=database.listar_categorias())


@bp.route("/<int:transacao_id>/excluir", methods=["POST"])
def excluir(transacao_id):
    database.deletar_transacao(transacao_id)
    flash("Transação excluída.", "ok")
    return redirect(url_for("lancamentos.listar"))