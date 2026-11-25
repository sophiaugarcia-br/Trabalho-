import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # gera imagens sem abrir janela
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

COR_ENTRADA = "#2E9E6B"
COR_SAIDA = "#D1495B"
COR_INVEST = "#6C5CE7"
COR_PRIMARIA = "#1F6F8B"
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def _brl(centavos):
    texto = f"{centavos / 100:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def grafico_colunas(rel, caminho):
    rotulos = [s["rotulo"] for s in rel.semanas]
    x = range(len(rotulos))
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar([i - 0.2 for i in x], [s["entradas"] / 100 for s in rel.semanas], 0.4,
           label="Entradas", color=COR_ENTRADA)
    ax.bar([i + 0.2 for i in x], [s["saidas"] / 100 for s in rel.semanas], 0.4,
           label="Saídas", color=COR_SAIDA)
    ax.set_xticks(list(x))
    ax.set_xticklabels(rotulos)
    ax.set_ylabel("R$")
    ax.set_title("Entradas e saídas por semana")
    ax.legend()
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


def grafico_pizza(rel, caminho):
    nomes = [c["categoria"] for c in rel.saidas_por_categoria]
    valores = [c["total_centavos"] / 100 for c in rel.saidas_por_categoria]
    fig, ax = plt.subplots(figsize=(5, 3.4))
    ax.pie(valores, labels=nomes, autopct="%1.0f%%", startangle=90)
    ax.set_title("Saídas por categoria")
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


def _tabela(cabecalho, linhas, larguras, cor):
    dados = [cabecalho] + linhas
    t = Table(dados, colWidths=larguras, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(cor)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
        ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
    ]))
    return t


def gerar_pdf(rel, caminho):
    estilos = getSampleStyleSheet()
    h2 = ParagraphStyle("h2", parent=estilos["Heading2"], textColor=colors.HexColor(COR_PRIMARIA))
    normal = estilos["Normal"]
    historia = []

    titulo = f"Finant — Relatório de {MESES[rel.mes - 1]} de {rel.ano}"
    historia += [Paragraph(titulo, estilos["Title"]), Spacer(1, 0.3 * cm)]

    # Resultado do mês (entradas x saídas, sem investimentos)
    historia.append(Paragraph("Resultado do mês", h2))
    historia.append(_tabela(
        ["Total de entradas", "Total de saídas", "Resultado"],
        [[_brl(rel.total_entradas), _brl(rel.total_saidas), f"{_brl(rel.resultado)} ({rel.situacao})"]],
        [5.5 * cm, 5.5 * cm, 6 * cm], COR_PRIMARIA))

    with tempfile.TemporaryDirectory() as pasta:
        pasta = Path(pasta)
        historia.append(Paragraph("Gráficos", h2))
        if rel.total_entradas or rel.total_saidas:
            grafico_colunas(rel, pasta / "colunas.png")
            historia.append(Image(str(pasta / "colunas.png"), width=15 * cm, height=7.5 * cm))
        if rel.saidas_por_categoria:
            grafico_pizza(rel, pasta / "pizza.png")
            historia.append(Image(str(pasta / "pizza.png"), width=11 * cm, height=7.5 * cm))
        if not (rel.total_entradas or rel.total_saidas):
            historia.append(Paragraph("Sem lançamentos neste mês.", normal))

        # Listagens
        historia.append(Paragraph("Entradas", h2))
        if rel.entradas:
            historia.append(_tabela(["Data", "Descrição", "Categoria", "Valor"],
                [[l["data"], l["descricao"], l["categoria"], _brl(l["valor_centavos"])] for l in rel.entradas],
                [2.5 * cm, 6.5 * cm, 4 * cm, 4 * cm], COR_ENTRADA))
        else:
            historia.append(Paragraph("Nenhuma entrada.", normal))

        historia.append(Paragraph("Saídas", h2))
        if rel.saidas:
            historia.append(_tabela(["Data", "Descrição", "Categoria", "Valor"],
                [[l["data"], l["descricao"], l["categoria"], _brl(l["valor_centavos"])] for l in rel.saidas],
                [2.5 * cm, 6.5 * cm, 4 * cm, 4 * cm], COR_SAIDA))
        else:
            historia.append(Paragraph("Nenhuma saída.", normal))

        # Metas abertas
        historia.append(Paragraph("Metas em aberto", h2))
        if rel.metas:
            historia.append(_tabela(["Produto", "Prazo", "Faltam", "Guardar por mês"],
                [[m["produto"], m["prazo"], _brl(m["faltante"]), _brl(m["por_mes"])] for m in rel.metas],
                [5 * cm, 3 * cm, 4 * cm, 5 * cm], COR_PRIMARIA))
        else:
            historia.append(Paragraph("Nenhuma meta em aberto.", normal))

        # Investimentos (bloco separado, fora do resultado acima)
        historia.append(Paragraph("Investimentos (valores brutos, separados do resultado)", h2))
        inv = rel.investimentos
        if inv["itens"]:
            historia.append(_tabela(["Investimento", "Taxa", "Lucro no mês", "Total no fim"],
                [[i["nome"], i["taxa_texto"], _brl(i["lucro_mes"]), _brl(i["total_fim"])] for i in inv["itens"]]
                + [["Total", "", _brl(inv["total_lucro"]), _brl(inv["total_final"])]],
                [5 * cm, 3.5 * cm, 4.2 * cm, 4.3 * cm], COR_INVEST))
        else:
            historia.append(Paragraph("Nenhum investimento ativo neste mês.", normal))

        doc = SimpleDocTemplate(str(caminho), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                                topMargin=2 * cm, bottomMargin=2 * cm, title=titulo)
        doc.build(historia)