import calendar
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from types import SimpleNamespace

# Dados fictícios (só em memória). taxa em % como texto: "12" = 12%
_INVEST = [
    SimpleNamespace(id=1, nome="CDB Banco X", valor_inicial_centavos=100000,
                    taxa="12", periodicidade_taxa="AA",
                    data_inicio=date(2026, 9, 1), data_resgate=None),
]
_proximo_id = 2


def _taxa_anual(inv):
    t = Decimal(inv.taxa) / 100
    if inv.periodicidade_taxa == "AM":
        t = (1 + t) ** 12 - 1
    return t


def _montante(inv, d):
    dias = (d - inv.data_inicio).days
    return Decimal(inv.valor_inicial_centavos) * (1 + _taxa_anual(inv)) ** (Decimal(dias) / Decimal(365))


def resumo_mes(ano, mes):
    primeiro = date(ano, mes, 1)
    ultimo = date(ano, mes, calendar.monthrange(ano, mes)[1])
    itens = []
    for inv in _INVEST:
        if inv.data_inicio > ultimo:
            continue
        if inv.data_resgate and inv.data_resgate < primeiro:
            continue
        ini = max(primeiro, inv.data_inicio)
        fim = min(ultimo, inv.data_resgate) if inv.data_resgate else ultimo
        lucro = _montante(inv, fim) - _montante(inv, ini)
        itens.append({
            "inv": inv,
            "lucro_mes": round(lucro),            # arredonda só no final
            "total_fim": round(_montante(inv, fim)),
        })
    return {
        "itens": itens,
        "total_lucro": sum(i["lucro_mes"] for i in itens),
        "total_final": sum(i["total_fim"] for i in itens),
    }


def cadastrar_investimento(dados):
    global _proximo_id
    erros = []

    nome = dados.get("nome", "").strip()
    if not nome:
        erros.append("Informe o nome do investimento.")

    valor = 0
    try:
        valor = round(Decimal(dados.get("valor", "").replace(",", ".")) * 100)
        if valor <= 0:
            erros.append("O valor aplicado deve ser maior que zero.")
    except InvalidOperation:
        erros.append("Valor aplicado inválido.")

    taxa = dados.get("taxa", "").replace(",", ".")
    try:
        if Decimal(taxa) <= 0:
            erros.append("A taxa deve ser maior que zero.")
    except InvalidOperation:
        erros.append("Taxa inválida.")

    period = dados.get("periodicidade_taxa")
    if period not in ("AA", "AM"):
        erros.append("Escolha se a taxa é ao ano ou ao mês.")

    inicio = resgate = None
    try:
        inicio = datetime.strptime(dados.get("data_inicio", ""), "%Y-%m-%d").date()
    except ValueError:
        erros.append("Data de início inválida.")
    if dados.get("data_resgate"):
        try:
            resgate = datetime.strptime(dados["data_resgate"], "%Y-%m-%d").date()
            if inicio and resgate < inicio:
                erros.append("O resgate não pode ser antes do início.")
        except ValueError:
            erros.append("Data de resgate inválida.")

    if erros:
        return erros

    _INVEST.append(SimpleNamespace(id=_proximo_id, nome=nome, valor_inicial_centavos=valor,
                                   taxa=taxa, periodicidade_taxa=period,
                                   data_inicio=inicio, data_resgate=resgate))
    _proximo_id += 1
    return []