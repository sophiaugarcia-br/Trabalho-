from dataclasses import dataclass
from datetime import date

@dataclass
class categoria: 
    nome: str
    tipo: str
    cor: str = "#FFFFFF"
    id: int | None = None

@dataclass
class transacao: 
    tipo = str
    descricao: str
    valor_centavos = int
    data = date
    categoria_id = int
    recorrencia_id = int
    id: int | None = None

@dataclass
class recorrencia: 
    tipo: str
    descricao: str
    valor_centavos: int
    data: date
    periodicidade: str
    dia: int
    data_inicio: date
    categoria_id: int
    data_fim: date | None = None
    id: int | None = None

@dataclass
class metas: 
    