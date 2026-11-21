from dataclasses import dataclass
from datetime import date

@dataclass
class Relatorio: 
    mes: str
    caminho_pdf: str
    gerado_em: date
    hash_dados: str

    def __post_init__(self):

        # Relatorio.mes

        
        # Relatorio.caminho_pdf

        
        # Relatorio.gerado_em

        
        # Relatorio.hash_dados

        