from dataclasses import dataclass
from datetime import date
from typing import Literal

@dataclass
class Previsao: 
    gerada_em: date
    saldo_projetado_centavos: int
    situacao: Literal["LUCRO", "EQUILIBRIO", "DIVIDA"]
    id: int | None = None

    def __post_init__(self):

        # Previsao.gerada_em

        
        # Previsao.saldo_projetado_centavos

        
        # Previsao.situacao

        
        # Previsao.id

        