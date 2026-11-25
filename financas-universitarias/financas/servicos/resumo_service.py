"""
Serviço de resumo: totais do mês, extrato com filtros, registro de
lançamentos e dados dos gráficos.

Convenções do projeto:
    - Dinheiro sempre em centavos (int).
    - Datas no formato AAAA-MM-DD.
    - Tipos de transação: "ENTRADA" e "SAIDA".
"""
from datetime import date

from financas.utils import datas, validacao
from financas.utils.dinheiro import para_centavos

TIPO_ENTRADA = "ENTRADA"
TIPO_SAIDA = "SAIDA"


# ---------------------------------------------------------------------------
# Funções auxiliares (começam com "_" porque são de uso interno do módulo)
# ---------------------------------------------------------------------------
def _periodo_do_mes(ano, mes):
    """Devolve (primeiro dia, último dia) do mês informado."""
    return datas.inicio_mes(ano, mes), datas.fim_mes(ano, mes)


def _dia_do_mes(transacao):
    """Devolve o dia (1 a 31) de uma transação, aceitando texto ou date."""
    data = transacao["data"]
    if isinstance(data, str):
        data = date.fromisoformat(data)  # "2026-11-24" -> date
    return data.day


def _semana_do_mes(dia):
    """Dias 1-7 = semana 1, 8-14 = semana 2, ..., 29-31 = semana 5."""
    return (dia - 1) // 7 + 1


def _em_reais(centavos):
    """Converte centavos em reais SÓ para o gráfico desenhar.

    Nenhuma conta financeira usa esse valor: ele vai direto para o Chart.js.
    """
    return centavos / 100


# ---------------------------------------------------------------------------
# 1) Resumo do mês (tela inicial)
# ---------------------------------------------------------------------------
def resumo_mes(trans_repo, ano, mes, hoje=None):
    """Totais do mês: entradas, saídas e saldo.

    No mês corrente, conta do dia 1º até hoje (regra do projeto).
    Em meses passados, conta o mês inteiro.

    Retorna um dicionário com valores em centavos.
    """
    if hoje is None:
        hoje = date.today()

    inicio, fim_do_mes = _periodo_do_mes(ano, mes)
    fim = min(fim_do_mes, hoje)  # não conta dias que ainda não chegaram

    total_entradas = 0
    total_saidas = 0
    quantidade = 0

    if fim >= inicio:  # mês futuro não tem lançamentos
        # None, None = sem filtro de tipo e sem filtro de categoria
        for transacao in trans_repo.listar((inicio, fim), None, None):
            quantidade += 1
            if transacao["tipo"] == TIPO_ENTRADA:
                total_entradas += transacao["valor_centavos"]
            elif transacao["tipo"] == TIPO_SAIDA:
                total_saidas += transacao["valor_centavos"]

    return {
        "ano": ano,
        "mes": mes,
        "entradas_centavos": total_entradas,
        "saidas_centavos": total_saidas,
        "saldo_centavos": total_entradas - total_saidas,
        "quantidade": quantidade,
    }


# ---------------------------------------------------------------------------
# 2) Extrato com filtros
# ---------------------------------------------------------------------------
def listar_extrato(trans_repo, filtros):
    """Lista os lançamentos do mês, do mais recente para o mais antigo.

    filtros é um dicionário com:
        "ano" e "mes"        (obrigatórios)
        "tipo"               (opcional: "ENTRADA" ou "SAIDA")
        "categoria_id"       (opcional)
    """
    periodo = _periodo_do_mes(filtros["ano"], filtros["mes"])

    tipo = filtros.get("tipo")
    if tipo not in (TIPO_ENTRADA, TIPO_SAIDA):
        tipo = None  # qualquer outro valor significa "sem filtro"

    categoria_id = filtros.get("categoria_id")

    transacoes = trans_repo.listar(periodo, tipo, categoria_id)
    return sorted(transacoes, key=lambda t: t["data"], reverse=True)


# ---------------------------------------------------------------------------
# 3) Registrar um lançamento (formulário de entrada/saída)
# ---------------------------------------------------------------------------
def registrar_lancamento(trans_repo, dados):
    """Valida e grava um lançamento novo.

    dados vem do formulário, tudo como texto:
        tipo, descricao, valor, data, categoria_id

    Retorna {"ok": True, "id": ..., "erros": []} se gravou, ou
    {"ok": False, "erros": [mensagens]} se algo estava errado.
    """
    # 1. Validações do formulário (campos obrigatórios, data válida...)
    erros = validacao.validar_lancamento(dados)
    if erros:
        return {"ok": False, "erros": erros}

    # 2. Converte o valor digitado ("12,50") para centavos (1250)
    try:
        valor_centavos = para_centavos(dados["valor"])
    except ValueError:
        return {"ok": False, "erros": ["Informe um valor válido."]}

    if valor_centavos <= 0:
        return {"ok": False, "erros": ["O valor deve ser maior que zero."]}

    # 3. Grava pelo repositório (único que fala com o banco)
    novo_id = trans_repo.inserir({
        "tipo": dados["tipo"],
        "descricao": dados["descricao"].strip(),
        "valor_centavos": valor_centavos,
        "data": validacao.normalizar_data(dados["data"]),  # sempre AAAA-MM-DD com zeros
        "categoria_id": dados.get("categoria_id"),
        "recorrencia_id": None,  # lançamento manual, não vem de recorrência
    })
    return {"ok": True, "id": novo_id, "erros": []}


# ---------------------------------------------------------------------------
# 4) Dados dos gráficos (a rota /api/graficos devolve isto como JSON)
# ---------------------------------------------------------------------------
def dados_graficos(trans_repo, ano, mes, filtro="saidas", categoria_id=None):
    """Monta os dados dos dois gráficos do painel.

    filtro: "entradas", "saidas" ou "investimentos".
    categoria_id: se informado, as colunas contam só essa categoria.

    Retorna um dicionário pronto para virar JSON:
        "colunas": totais por semana do mês (em reais, só para desenhar)
        "pizza":   total por categoria
    """
    if filtro == "investimentos":
        # Investimentos têm regra própria, por isso chamamos o outro serviço.
        from financas.servicos import investimento_service
        return {
            "filtro": filtro,
            "investimentos": investimento_service.resumo_mes(ano, mes),
        }

    periodo = _periodo_do_mes(ano, mes)

    # --- Gráfico de colunas: total por semana ---------------------------
    entradas_por_semana = [0, 0, 0, 0, 0]  # semanas 1 a 5, em centavos
    saidas_por_semana = [0, 0, 0, 0, 0]

    for transacao in trans_repo.listar(periodo, None, categoria_id):
        indice = _semana_do_mes(_dia_do_mes(transacao)) - 1
        if transacao["tipo"] == TIPO_ENTRADA:
            entradas_por_semana[indice] += transacao["valor_centavos"]
        elif transacao["tipo"] == TIPO_SAIDA:
            saidas_por_semana[indice] += transacao["valor_centavos"]

    colunas = {"rotulos": ["Semana %d" % n for n in range(1, 6)]}
    if filtro == "entradas":
        colunas["entradas"] = [_em_reais(v) for v in entradas_por_semana]
    else:  # "saidas" (padrão)
        colunas["saidas"] = [_em_reais(v) for v in saidas_por_semana]

    # --- Gráfico de pizza: total por categoria --------------------------
    tipo_pizza = TIPO_ENTRADA if filtro == "entradas" else TIPO_SAIDA
    pizza = {"ids": [], "rotulos": [], "valores": [], "cores": []}

    for linha in trans_repo.somar_por_categoria(periodo, tipo_pizza):
        pizza["ids"].append(linha["categoria_id"])  # o clique na fatia usa o id
        pizza["rotulos"].append(linha["nome"])
        pizza["valores"].append(_em_reais(linha["total_centavos"]))
        pizza["cores"].append(linha["cor"])

    return {"filtro": filtro, "colunas": colunas, "pizza": pizza}
