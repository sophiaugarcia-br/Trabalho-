from dataclasses import dataclass
from datetime import date

@dataclass
class Categoria: 
    nome: str
    tipo: str
    cor: str = "#FFFFFF"
    id: int | None = None