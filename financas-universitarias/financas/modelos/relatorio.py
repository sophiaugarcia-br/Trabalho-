from dataclasses import dataclass
from datetime import date

@dataclass
class relatorio: 
    mes: str
    caminho_pdf: str
    gerado_em: date
    hash_dados: str