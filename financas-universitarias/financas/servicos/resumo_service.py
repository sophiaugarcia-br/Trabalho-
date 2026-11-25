"""
Serviço de resumo: totais do mês, extrato com filtros, registro de
lançamentos e dados dos gráficos.

Convenções do projeto:
- Dinheiro sempre em centavos (int).
- Datas no formato AAAA-MM-DD.
- Tipos de transação: "ENTRADA" e "SAIDA".
"""
from datetime import date
from typing import Any, Dict, List, Optional

from financas.utils import datas, validacao
from financas.utils.dinheiro import para_centavos

TIPO_ENTRADA = "ENTRADA"
TIPO_SAIDA = "SAIDA"


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def _campo(obj: Any, chave: str) -> Any:
    """Lê um campo aceitando tanto dicionário quanto objeto/namespace."""
    return obj[chave] if isinstance(obj, dict) else getattr(obj, chave)


def _periodo_do_mes(ano: int, mes: int):
    """Devolve (primeiro dia, último dia) do mês informado."""
    return datas.inicio_mes(ano, mes), datas.fim_mes(ano, mes)


def _dia_do_mes(transacao: Any) -> int:
    """Devolve o dia (1 a 31) de uma transação, aceitando texto ou date."""
    dt = _campo(transacao, "data")
    if isinstance(dt, str):
        dt = date.fromisoformat(dt)
    return dt.day


def _semana_do_mes(dia: int) -> int:
    """Dias 1-7 = semana 1, 8-14 = semana 2, ..., 29-31 = semana 5.

    Retorna o índice de 0 a 4.
    """
    semana = (dia - 1) // 7
    return min(4, max(0, semana))


def _em_reais(centavos: int) -> float:
    """Converte centavos em reais SÓ para o gráfico desenhar."""
    return centavos / 100.0


# ---------------------------------------------------------------------------
# 1) Resumo do mês (tela inicial)
# ---------------------------------------------------------------------------
def resumo_mes(
    trans_repo: Any,
    ano: int,
    mes: int,
    hoje: Optional[date] = None,
) -> Dict[str, int]:
    """Totais do mês: entradas, saídas e saldo em centavos."""
    if hoje is None:
        hoje = date.today()

    inicio, fim_do_mes = _periodo_do_mes(ano, mes)

    if inicio > hoje:
        return {
            "ano": ano,
            "mes": mes,
            "entradas_centavos": 0,
            "saidas_centavos": 0,
            "saldo_centavos": 0,
            "quantidade": 0,
        }

    if ano == hoje.year and mes == hoje.month:
        fim = min(fim_do_mes, hoje)
    else:
        fim = fim_do_mes

    total_entradas = 0
    total_saidas = 0
    quantidade = 0

    for transacao in trans_repo.listar((inicio, fim), None, None):
        quantidade += 1
        tipo = _campo(transacao, "tipo")
        valor = _campo(transacao, "valor_centavos")
        if tipo == TIPO_ENTRADA:
            total_entradas += valor
        elif tipo == TIPO_SAIDA:
            total_saidas += valor

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
def listar_extrato(trans_repo: Any, filtros: Dict[str, Any]) -> List[Any]:
    """Lista os lançamentos do mês, do mais recente para o mais antigo."""
    periodo = _periodo_do_mes(filtros["ano"], filtros["mes"])

    tipo = filtros.get("tipo")
    if tipo not in (TIPO_ENTRADA, TIPO_SAIDA):
        tipo = None

    categoria_id = filtros.get("categoria_id")

    transacoes = trans_repo.listar(periodo, tipo, categoria_id)
    return sorted(transacoes, key=lambda t: str(_campo(t, "data")), reverse=True)


# ---------------------------------------------------------------------------
# 3) Registrar um lançamento (formulário de entrada/saída)
# ---------------------------------------------------------------------------
def registrar_lancamento(trans_repo: Any, dados: Dict[str, Any]) -> Dict[str, Any]:
    """Valida e grava um lançamento novo."""
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
        "data": validacao.normalizar_data(dados["data"]),
        "categoria_id": dados.get("categoria_id"),
        "recorrencia_id": None,
    })
    return {"ok": True, "id": novo_id, "erros": []}


# ---------------------------------------------------------------------------
# 4) Dados dos gráficos
# ---------------------------------------------------------------------------
def dados_graficos(
    trans_repo: Any,
    ano: int,
    mes: int,
    filtro: str = "saidas",
    categoria_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Monta os dados dos dois gráficos do painel."""
    if filtro == "investimentos":
        from financas.servicos import investimento_service
        return {
            "filtro": filtro,
            "colunas": {"rotulos": [], "investimentos": []},
            "pizza": {"ids": [], "rotulos": [], "valores": [], "cores": []},
            "resumo": investimento_service.resumo_mes(trans_repo, ano, mes),
        }

    periodo = _periodo_do_mes(ano, mes)
    tipo_filtro = TIPO_ENTRADA if filtro == "entradas" else TIPO_SAIDA

    # --- Gráfico de colunas: total por semana ---------------------------
    totais_por_semana = [0, 0, 0, 0, 0]

    for transacao in trans_repo.listar(periodo, tipo_filtro, categoria_id):
        indice = _semana_do_mes(_dia_do_mes(transacao))
        totais_por_semana[indice] += _campo(transacao, "valor_centavos")

    chave_coluna = "entradas" if filtro == "entradas" else "saidas"
    colunas = {
        "rotulos": [f"Semana {n}" for n in range(1, 6)],
        chave_coluna: [_em_reais(v) for v in totais_por_semana],
    }

    # --- Gráfico de pizza: total por categoria --------------------------
    pizza: Dict[str, List[Any]] = {"ids": [], "rotulos": [], "valores": [], "cores": []}

    for linha in trans_repo.somar_por_categoria(periodo, tipo_filtro):
        pizza["ids"].append(_campo(linha, "categoria_id"))
        pizza["rotulos"].append(_campo(linha, "nome"))
        pizza["valores"].append(_em_reais(_campo(linha, "total_centavos")))
        pizza["cores"].append(_campo(linha, "cor"))

    return {"filtro": filtro, "colunas": colunas, "pizza": pizza}