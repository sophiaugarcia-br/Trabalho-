from dataclasses import dataclass
from datetime import date, datetime

@dataclass
class Relatorio: 
    mes: str
    caminho_pdf: str
    gerado_em: date
    hash_dados: str

    def __post_init__(self):

        # Relatorio.mes
        if not isinstance(self.mes, str): 
            raise TypeError(f"Relatorio.mes deve ser str ('AAAA-MM'), mas recebeu {type(self.mes).__name__}.")
        self.mes = self.mes.strip()
        try: 
            if len(self.mes) != 7: 
                raise ValueError(f"Valor inválido: Relatorio.mes não está no formato (AAAA-MM).")
            datetime.strptime(self.mes, "%Y-%m")
        except ValueError: 
            raise ValueError(f"Mês inválido: {self.mes!r}. Use o formato AAAA-MM (ex: '2026-11').")
        
        # Relatorio.caminho_pdf
        if not isinstance(self.caminho_pdf, str):
            raise TypeError(f"Relatorio.caminho_pdf deve ser declarado e ser uma string.")
        self.caminho_pdf = self.caminho_pdf.strip()
        if not self.caminho_pdf:
            raise ValueError("Erro! Relatorio.caminho_pdf não pode ser vazio.")
        
        # Relatorio.gerado_em
        if isinstance(self.gerado_em, str): 
            self.gerado_em = self.gerado_em.strip() # type: ignore
            try: 
                self.gerado_em = date.fromisoformat(self.gerado_em) # type: ignore
            except ValueError: raise ValueError(f"{self.gerado_em!r} não é um valor de gerado_em válido. Use o formato AAAA-MM-DD.") # type: ignore
        if type(self.gerado_em) is not date: raise TypeError(f"Tipo errôneo de dado. {type(self.gerado_em).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")
        
        # Relatorio.hash_dados
        if not isinstance(self.hash_dados, str):
            raise TypeError(f"Relatorio.hash_dados deve ser declarado e ser uma string.")
        self.hash_dados = self.hash_dados.strip()
        if not self.hash_dados:
            raise ValueError("Relatorio.hash_dados não pode ficar vazio.")