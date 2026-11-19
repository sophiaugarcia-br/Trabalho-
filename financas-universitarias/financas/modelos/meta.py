from dataclasses import dataclass
from datetime import date

@dataclass
class meta: 
    produto: str
    preco_centavos: int
    criada_em: date
    guardado_centavos: int
    status: str
    concluida_em: date | None = None
    prazo: date | None = None
    id: int | None = None