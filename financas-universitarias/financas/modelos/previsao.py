from dataclasses import dataclass
from datetime import date

@dataclass
class Previsao: 
    gerada_em: date
    saldo_projetado_centavos: int
    situacao: str
    id: int | None = None