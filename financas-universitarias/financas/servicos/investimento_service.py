from dataclasses import dataclass
from decimal import Decimal
from financas.utils.datas import inicio_mes, fim_mes
from financas.utils.dinheiro import arredondar_centavos

DIAS_NO_ANO = Decimal(365)

@dataclass(frozen=True)
class RendimentoMes:
    nome: str
    lucro_centavos: int
    total_centavos: int

@dataclass(frozen=True)
class ResumoInvestimentos:
    itens: list
    lucro_centavos: int
    total_centavos: int

def taxa_anual(inv):
    taxa = Decimal(inv.taxa)
    if inv.periodicidade_taxa == "AA":
        return taxa
    if inv.periodicidade_taxa == "AM":
        return (1 + taxa) ** 12 - 1
    raise ValueError(f"Periodicidade inválida: {inv.periodicidade_taxa!r}")

def montante(inv, data):
    dias = max(0, (data - inv.data_inicio).days)
    expoente = Decimal(dias) / DIAS_NO_ANO
    fator = (1 + taxa_anual(inv)) ** expoente
    return Decimal(inv.valor_inicial_centavos) * fator

def ativo_no_mes(inv, ano, mes):
    comecou = inv.data_inicio <= fim_mes(ano, mes)
    nao_resgatado = inv.data_resgate is None or inv.data_resgate >= inicio_mes(ano, mes)
    return comecou and nao_resgatado

def ativos_no_mes(investimentos, ano, mes):
    return [i for i in investimentos if ativo_no_mes(i, ano, mes)]

def rendimento_no_mes(inv, ano, mes):
    if not ativo_no_mes(inv, ano, mes):
        return None
    inicio_efetivo = max(inicio_mes(ano, mes), inv.data_inicio)
    fim_efetivo = fim_mes(ano, mes)
    if inv.data_resgate is not None:
        fim_efetivo = min(fim_efetivo, inv.data_resgate)

    total_no_fim = montante(inv, fim_efetivo)
    lucro = total_no_fim - montante(inv, inicio_efetivo)
    return RendimentoMes(inv.nome,
                         arredondar_centavos(lucro),
                         arredondar_centavos(total_no_fim))

def resumo_mes(investimentos, ano, mes):
    todos = (rendimento_no_mes(i, ano, mes) for i in investimentos)
    itens = [r for r in todos if r is not None]
    return ResumoInvestimentos(
        itens,
        sum(r.lucro_centavos for r in itens),
        sum(r.total_centavos for r in itens),
    )
