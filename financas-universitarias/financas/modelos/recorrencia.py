from dataclasses import dataclass
from datetime import date

@dataclass
class Recorrencia: 
    tipo: str
    descricao: str
    valor_centavos: int
    periodicidade: str
    dia: int
    data_inicio: date
    categoria_id: int
    data_fim: date | None = None
    id: int | None = None