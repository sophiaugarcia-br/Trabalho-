import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import database
from financas.servicos import pdf_service
# TEMPORÁRIO: trocar pelos serviços reais quando existirem
from financas.rotas import _mocks as meta_service
from financas.rotas import _mocks_investimentos as investimento_service

MESES = pdf_service.MESES
PASTA_PDFS = Path(__file__).resolve().parents[2] / "relatorios"


@dataclass(frozen=True)
class RelatorioMensal:
    ano: int
    mes: int
    total_entradas: int        # tudo em centavos
    total_saidas: int
    resultado: int
    situacao: str              # "LUCRO", "DÍVIDA" ou "NEUTRO"
    entradas: list
    saidas: list
    saidas_por_categoria: list
    semanas: list
    metas: list
    investimentos: dict


def _data_br(iso):
    return f"{iso[8:10]}/{iso[5:7]}/{iso[0:4]}"


def montar_relatorio(ano, mes):
    transacoes = sorted(database.listar_transacoes(mes=mes, ano=ano),
                        key=lambda t: (t["data"], t["id"]))

    entradas, saidas, por_categoria = [], [], {}
    n_semanas = (calendar_dias(ano, mes) - 1) // 7 + 1
    semanas = [{"rotulo": f"Sem {i}", "entradas": 0, "saidas": 0} for i in range(1, n_semanas + 1)]

    for t in transacoes:
        centavos = round(t["valor"] * 100)
        item = {"data": _data_br(t["data"]), "descricao": t["descricao"],
                "categoria": t["categoria"], "valor_centavos": centavos}
        semana = semanas[(int(t["data"][8:10]) - 1) // 7]
        if t["tipo"] == "Receita":
            entradas.append(item)
            semana["entradas"] += centavos
        else:
            saidas.append(item)
            semana["saidas"] += centavos
            por_categoria[t["categoria"]] = por_categoria.get(t["categoria"], 0) + centavos

    total_entradas = sum(e["valor_centavos"] for e in entradas)
    total_saidas = sum(s["valor_centavos"] for s in saidas)
    resultado = total_entradas - total_saidas
    situacao = "LUCRO" if resultado > 0 else "DÍVIDA" if resultado < 0 else "NEUTRO"

    # Metas: por enquanto, as abertas hoje (o mock não guarda histórico)
    metas = [{
        "produto": i["meta"].produto,
        "prazo": i["meta"].prazo.strftime("%d/%m/%Y"),
        "faltante": i["plano"].faltante,
        "por_mes": i["plano"].por_mes,
    } for i in meta_service.painel_metas(date.today())["itens"]]

    # Investimentos: bloco separado, nunca entra no resultado acima
    inv = investimento_service.resumo_mes(ano, mes)
    investimentos = {
        "itens": [{
            "nome": i["inv"].nome,
            "taxa_texto": f'{i["inv"].taxa}% ' + ("a.a." if i["inv"].periodicidade_taxa == "AA" else "a.m."),
            "lucro_mes": i["lucro_mes"],
            "total_fim": i["total_fim"],
        } for i in inv["itens"]],
        "total_lucro": inv["total_lucro"],
        "total_final": inv["total_final"],
    }

    return RelatorioMensal(
        ano=ano, mes=mes,
        total_entradas=total_entradas, total_saidas=total_saidas,
        resultado=resultado, situacao=situacao,
        entradas=entradas, saidas=saidas,
        saidas_por_categoria=[{"categoria": c, "total_centavos": v}
                              for c, v in sorted(por_categoria.items(), key=lambda x: -x[1])],
        semanas=semanas, metas=metas, investimentos=investimentos,
    )


def calendar_dias(ano, mes):
    import calendar
    return calendar.monthrange(ano, mes)[1]


def hash_relatorio(rel):
    texto = json.dumps(asdict(rel), sort_keys=True, default=str)
    return hashlib.sha256(texto.encode()).hexdigest()


def meses_disponiveis(hoje=None):
    """Do mês da primeira transação até o mês atual, do mais novo para o mais antigo."""
    hoje = hoje or date.today()
    datas = [t["data"] for t in database.listar_transacoes()]
    inicio = min(datas) if datas else hoje.isoformat()
    ano, mes = int(inicio[:4]), int(inicio[5:7])
    meses = []
    while (ano, mes) <= (hoje.year, hoje.month):
        meses.append((ano, mes))
        mes += 1
        if mes == 13:
            ano, mes = ano + 1, 1
    return list(reversed(meses))


def garantir_pdf(ano, mes):
    """Gera o PDF do mês se não existir ou se os dados mudaram. Devolve o caminho."""
    rel = montar_relatorio(ano, mes)
    h = hash_relatorio(rel)
    caminho = PASTA_PDFS / f"{ano}-{mes:02d}.pdf"
    arquivo_hash = caminho.with_suffix(".hash")

    if not caminho.exists() or not arquivo_hash.exists() or arquivo_hash.read_text() != h:
        PASTA_PDFS.mkdir(exist_ok=True)
        pdf_service.gerar_pdf(rel, caminho)
        arquivo_hash.write_text(h)
    return caminho


def gerar_pendentes():
    """Chamada ao abrir o programa: atualiza os PDFs de todos os meses."""
    for ano, mes in meses_disponiveis():
        garantir_pdf(ano, mes)