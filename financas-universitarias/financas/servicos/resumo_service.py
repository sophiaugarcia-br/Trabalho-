
from datetime import date
from financas.utils import datas, validacao
from financas.utils.dinheiro import para_centavos

TIPO_ENTRADA = "ENTRADA"
TIPO_SAIDA = "SAIDA"

def _periodo_do_mes(ano, mes):
    return datas.inicio_mes(ano, mes), datas.fim_mes(ano, mes)

def _dia_do_mes(transacao):
    data = transacao["data"]
    if isinstance(data, str):
        data = date.fromisoformat(data)  
    return data.day

def _semana_do_mes(dia):
    return (dia - 1) // 7 + 1

def _em_reais(centavos):
    return centavos / 100



# 1) Resumo do mês 
# ---------
def resumo_mes(trans_repo, ano, mes, hoje=None):
    if hoje is None:
        hoje = date.today()

    inicio, fim_do_mes = _periodo_do_mes(ano, mes)
    fim = min(fim_do_mes, hoje) 

    total_entradas = 0
    total_saidas = 0
    quantidade = 0

    if fim >= inicio:  
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

# 2) Extrato com filtros
# ---------
def listar_extrato(trans_repo, filtros):
    periodo = _periodo_do_mes(filtros["ano"], filtros["mes"])

    tipo = filtros.get("tipo")
    if tipo not in (TIPO_ENTRADA, TIPO_SAIDA):
        tipo = None  

    categoria_id = filtros.get("categoria_id")

    transacoes = trans_repo.listar(periodo, tipo, categoria_id)
    return sorted(transacoes, key=lambda t: t["data"], reverse=True)


# 3) Registrar um lançamento 
# --------
def registrar_lancamento(trans_repo, dados):
    erros = validacao.validar_lancamento(dados)
    if erros:
        return {"ok": False, "erros": erros}
    try:
        valor_centavos = para_centavos(dados["valor"])
    except ValueError:
        return {"ok": False, "erros": ["Informe um valor válido."]}

    if valor_centavos <= 0:
        return {"ok": False, "erros": ["O valor deve ser maior que zero."]}
    novo_id = trans_repo.inserir({
        "tipo": dados["tipo"],
        "descricao": dados["descricao"].strip(),
        "valor_centavos": valor_centavos,
        "data": dados["data"],
        "categoria_id": dados.get("categoria_id"),
        "recorrencia_id": None,  
    })
    return {"ok": True, "id": novo_id, "erros": []}


# 4) Dados dos gráficos 
# ---------------------
def dados_graficos(trans_repo, ano, mes, filtro="saidas", categoria_id=None):
    if filtro == "investimentos":
        from financas.servicos import investimento_service
        return {
            "filtro": filtro,
            "investimentos": investimento_service.resumo_mes(ano, mes),
        }

    periodo = _periodo_do_mes(ano, mes)

    # --- Gráfico: total por semana ---
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

    # --- Gráfico: total por categoria --
    tipo_pizza = TIPO_ENTRADA if filtro == "entradas" else TIPO_SAIDA
    pizza = {"ids": [], "rotulos": [], "valores": [], "cores": []}

    for linha in trans_repo.somar_por_categoria(periodo, tipo_pizza):
        pizza["ids"].append(linha["categoria_id"])  # o clique na fatia usa o id
        pizza["rotulos"].append(linha["nome"])
        pizza["valores"].append(_em_reais(linha["total_centavos"]))
        pizza["cores"].append(linha["cor"])

    return {"filtro": filtro, "colunas": colunas, "pizza": pizza}
