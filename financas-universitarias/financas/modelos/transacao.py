from dataclasses import dataclass
from datetime import date

@dataclass
class Transacao: 
    tipo: str
    descricao: str
    valor_centavos: int
    data: date
    categoria_id: int
    recorrencia_id: int | None = None
    id: int | None = None