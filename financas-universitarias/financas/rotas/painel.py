from flask import Blueprint, render_template
import database

bp = Blueprint("painel", __name__)


@bp.route("/")
def index():
    despesas_cat = database.despesas_por_categoria_mes_atual()

    return render_template(
        "painel.html",
        resumo=database.resumo_mes_atual(),
        chart_labels=[d["categoria"] for d in despesas_cat],
        chart_values=[d["total"] for d in despesas_cat],
    )
