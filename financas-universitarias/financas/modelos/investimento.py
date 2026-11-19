from dataclasses import dataclass
from decimal import Decimal
from datetime import date

@dataclass
class Investimento: 
    nome: str
    valor_inicial_centavos: int
    taxa: Decimal
    periodicidade_taxa: str
    data_inicio: date
    data_resgate: date | None = None
    id: int | None = None