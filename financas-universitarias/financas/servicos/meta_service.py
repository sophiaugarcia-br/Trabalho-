
import math
from dataclasses import dataclass
from datetime import date
from typing import Optional

from financas.modelos.meta import Meta
from financas.repositorios import meta_repo as repo_metas_real 
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


def _normalizar_data(valor: date | str | None) -> Optional[date]:
    if valor is None or isinstance(valor, date):
        return valor
    return date.fromisoformat(valor)


def calcular_plano(meta, hoje):
    """Calcula quanto guardar por semana e por mês para atingir a meta no prazo."""
    prazo = _normalizar_data(meta.prazo)
    faltante = max(0, meta.preco_centavos - meta.guardado_centavos)
    dias = (prazo - hoje).days

    semanas = max(1, math.ceil(dias / 7))
    meses = max(1, math.ceil(dias / 30))

    return PlanoMeta(
        faltante=faltante,
        dias=dias,
        semanas=semanas,
        meses=meses,
        por_semana=dividir_centavos(faltante, semanas),
        por_mes=dividir_centavos(faltante, meses),
        atingida=faltante == 0,
        vencida=dias <= 0,
    )


def viabilidade(planos, sobra_media_centavos):
    """Verifica se a soma das metas cabe na sobra média mensal."""
    total = sum(p.por_mes for p in planos)
    folga = sobra_media_centavos - total
    return Viabilidade(total, sobra_media_centavos, folga, folga >= 0)


# ---------------------------------------------------------------------------
# Integração com o repositório de metas
# ---------------------------------------------------------------------------
def criar_meta(
    produto: str,
    preco_centavos: int,
    prazo: date | str,
    guardado_centavos: int = 0,
    criada_em: Optional[date] = None,
    repo=repo_metas_real,
) -> Meta:
    """Cria uma nova meta aberta no repositório."""
    nova = Meta(
        id=None,
        produto=produto.strip(),
        preco_centavos=int(preco_centavos),
        criada_em=criada_em or date.today(),
        guardado_centavos=int(guardado_centavos),
        status="ABERTA",
        concluida_em=None,
        prazo=_normalizar_data(prazo),
    )
    return repo.criar(nova)


def guardar_valor_meta(
    meta_id: int,
    valor_centavos: int,
    hoje: Optional[date] = None,
    repo=repo_metas_real,
) -> Optional[Meta]:
    """Soma um valor guardado à meta e marca como CONCLUIDA se atingir o preço."""
    meta = repo.buscar_por_id(meta_id)
    if meta is None:
        return None

    meta.guardado_centavos += int(valor_centavos)
    if meta.guardado_centavos >= meta.preco_centavos:
        meta.status = "CONCLUIDA"
        if meta.concluida_em is None:
            meta.concluida_em = hoje or date.today()

    repo.atualizar(meta)
    return meta


def painel_metas(
    hoje: Optional[date] = None,
    sobra_media_centavos: int = 0,
    repo=repo_metas_real,
) -> dict:
    """Monta o painel das metas abertas com planos individuais e viabilidade."""
    data_ref = hoje or date.today()
    abertas = repo.listar_por_status("ABERTA")
    itens = [
        {"meta": m, "plano": calcular_plano(m, data_ref)}
        for m in abertas
    ]
    planos = [item["plano"] for item in itens]
    return {
        "itens": itens,
        "viabilidade": viabilidade(planos, sobra_media_centavos),
    }
