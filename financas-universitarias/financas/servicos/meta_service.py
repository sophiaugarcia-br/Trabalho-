
"""
Regras de negócio das metas de poupança (lista de produtos desejados).

Para cada meta, calcula quanto guardar por semana e por mês até o prazo.
Também verifica se todas as metas abertas cabem, juntas, na sobra média mensal.

Convenções do projeto: dinheiro em centavos (int) e prazos como date.
Este módulo não importa Flask nem acessa o banco.
"""
import math
from dataclasses import dataclass

from financas.utils.dinheiro import dividir_centavos


@dataclass(frozen=True)
class PlanoMeta:
    """Resultado do cálculo de uma meta (imutável por causa do frozen=True)."""
    faltante: int      # centavos que ainda faltam para chegar ao preço
    dias: int          # dias entre hoje e o prazo (zero ou negativo se venceu)
    semanas: int       # semanas até o prazo (mínimo 1)
    meses: int         # meses até o prazo, contando 30 dias por mês (mínimo 1)
    por_semana: int    # centavos a guardar por semana
    por_mes: int       # centavos a guardar por mês
    atingida: bool     # True se já guardou o suficiente (faltante == 0)
    vencida: bool      # True se o prazo é hoje ou já passou


@dataclass(frozen=True)
class Viabilidade:
    """Resultado da comparação entre as metas e a sobra média mensal."""
    total_mensal: int  # soma do por_mes de todas as metas (centavos)
    sobra_media: int   # sobra média mensal: entradas menos saídas (centavos)
    folga: int         # sobra_media - total_mensal (negativa = não cabe)
    viavel: bool       # True se folga >= 0


def calcular_plano(meta, hoje):
    """Calcula quanto guardar por semana e por mês para atingir a meta no prazo.

    meta deve ter: preco_centavos, guardado_centavos e prazo (date).
    hoje é um date (passado como parâmetro para facilitar os testes).
    Devolve um PlanoMeta.
    """
    # max(0, ...) evita faltante negativo se já guardou mais do que o preço
    faltante = max(0, meta.preco_centavos - meta.guardado_centavos)
    dias = (meta.prazo - hoje).days

    # math.ceil arredonda para cima; max(1, ...) evita dividir por zero
    # quando o prazo é hoje ou já passou
    semanas = max(1, math.ceil(dias / 7))
    meses = max(1, math.ceil(dias / 30))

    return PlanoMeta(
        faltante=faltante,
        dias=dias,
        semanas=semanas,
        meses=meses,
        por_semana=dividir_centavos(faltante, semanas),  # arredonda ao centavo
        por_mes=dividir_centavos(faltante, meses),
        atingida=faltante == 0,
        vencida=dias <= 0,
    )


def viabilidade(planos, sobra_media_centavos):
    """Verifica se a soma das metas cabe na sobra média mensal.

    As metas competem pela mesma sobra, por isso a conta é conjunta:
    soma-se o por_mes de todos os planos e compara-se com a sobra.
    planos é uma lista de PlanoMeta; sobra_media_centavos é um int.
    """
    total = sum(p.por_mes for p in planos)
    folga = sobra_media_centavos - total
    return Viabilidade(total, sobra_media_centavos, folga, folga >= 0)
