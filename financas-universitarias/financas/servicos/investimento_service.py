
"""
Regras de negócio dos investimentos de renda fixa com taxa fixa.

Calcula o montante com juros compostos por dias corridos e o lucro de cada
mês. O aporte não conta como saída: o rendimento aparece em bloco separado.

Convenções do projeto: dinheiro em centavos (int), taxas em Decimal e datas
como date. 
"""
from dataclasses import dataclass
from decimal import Decimal

from financas.utils.datas import inicio_mes, fim_mes
from financas.utils.dinheiro import arredondar_centavos

DIAS_NO_ANO = Decimal(365)  # juros compostos por dias corridos, ano de 365 dias


@dataclass(frozen=True)
class RendimentoMes:
    """Rendimento de um investimento em um mês (valores em centavos)."""
    nome: str
    lucro_centavos: int   # quanto rendeu dentro do mês
    total_centavos: int   # valor total do investimento no fim do período


@dataclass(frozen=True)
class ResumoInvestimentos:
    """Resumo de todos os investimentos ativos em um mês."""
    itens: list           # lista de RendimentoMes, um por investimento ativo
    lucro_centavos: int   # soma dos lucros do mês
    total_centavos: int   # soma dos totais no fim do mês


def taxa_anual(inv):
    """Devolve a taxa anual (Decimal) do investimento.

    A taxa vem como fração (0.12 = 12%). Se foi informada ao mês (AM),
    converte para ano com juros compostos: (1 + taxa) ** 12 - 1.
    Levanta ValueError se a periodicidade não for AA nem AM.
    """
    taxa = Decimal(inv.taxa)  # a taxa é guardada como texto, para não perder precisão
    if inv.periodicidade_taxa == "AA":
        return taxa
    if inv.periodicidade_taxa == "AM":
        return (1 + taxa) ** 12 - 1
    raise ValueError(f"Periodicidade inválida: {inv.periodicidade_taxa!r}")


def montante(inv, data):
    """Valor do investimento na data informada, em centavos (Decimal).

    Fórmula: P * (1 + taxa_anual) ** (dias / 365), com dias corridos
    desde o início. Datas anteriores ao início contam como zero dia.
    O arredondamento só acontece no final, em quem chama a função.
    """
    dias = max(0, (data - inv.data_inicio).days)
    expoente = Decimal(dias) / DIAS_NO_ANO
    fator = (1 + taxa_anual(inv)) ** expoente
    return Decimal(inv.valor_inicial_centavos) * fator


def ativo_no_mes(inv, ano, mes):
    """True se o investimento aparece no mês: começou até o fim do mês
    e não foi resgatado antes do primeiro dia do mês."""
    comecou = inv.data_inicio <= fim_mes(ano, mes)
    nao_resgatado = inv.data_resgate is None or inv.data_resgate >= inicio_mes(ano, mes)
    return comecou and nao_resgatado


def ativos_no_mes(investimentos, ano, mes):
    """Filtra a lista, mantendo só os investimentos ativos no mês."""
    return [i for i in investimentos if ativo_no_mes(i, ano, mes)]


def rendimento_no_mes(inv, ano, mes):
    """Calcula o rendimento do investimento no mês, ou None se não estava ativo.

    O período do mês vai do maior entre o dia 1º e o início do investimento
    até o menor entre o último dia do mês e o resgate (se houver).
    """
    if not ativo_no_mes(inv, ano, mes):
        return None
    inicio_efetivo = max(inicio_mes(ano, mes), inv.data_inicio)
    fim_efetivo = fim_mes(ano, mes)
    if inv.data_resgate is not None:
        fim_efetivo = min(fim_efetivo, inv.data_resgate)

    total_no_fim = montante(inv, fim_efetivo)
    lucro = total_no_fim - montante(inv, inicio_efetivo)  # rendeu no período
    return RendimentoMes(inv.nome,
                         arredondar_centavos(lucro),
                         arredondar_centavos(total_no_fim))


def resumo_mes(investimentos, ano, mes):
    """Resumo dos investimentos do mês: um item por investimento ativo,
    mais o lucro total e o valor total somados."""
    # generator: calcula um rendimento por vez; None = não estava ativo
    todos = (rendimento_no_mes(i, ano, mes) for i in investimentos)
    itens = [r for r in todos if r is not None]
    return ResumoInvestimentos(
        itens,
        sum(r.lucro_centavos for r in itens),
        sum(r.total_centavos for r in itens),
    )
