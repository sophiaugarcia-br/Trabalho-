

import math
from dataclasses import dataclass
from financas.utils.dinheiro import dividir_centavos

@dataclass(frozen=True)
class PlanoMeta:
    faltante: int        
    dias: int         
    semanas: int
    meses: int
    por_semana: int     
    por_mes: int        
    atingida: bool      
    vencida: bool       
@dataclass(frozen =True)
class Viabilidade:
    total_mensal: int
    total_mensal: int    
    sobra_media: int   
    folga: int          
    viavel: bool

def calcular_plano(meta, hoje):
    faltante = max(0, meta.preco_centavos - meta.guardado_centavos)
    dias = (meta.prazo - hoje).days
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
    total = sum(p.por_mes for p in planos)
    folga = sobra_media_centavos - total
    return Viabilidade(total, sobra_media_centavos, folga, folga >= 0)
