from dataclasses import dataclass
from datetime import date, datetime

"""  Este arquivo cria a classe (molde) 'Relatorio' para todo dado (objeto) que é um relatorio, cujo qual tem um mes, caminho_pdf, gerado_em, hash_dados (ex: 2026-09, 'C:/users/user/rel.pdf', 2026-09-02, 'df5g15b5c6e1h2v22g2f5jhhg1d5wq5r2i2l2'). Isso serve para definir e aceitar universalmente, em variáveis daquele relatorio, apenas um tipo de dado por atributo.  """

@dataclass
class Relatorio: 
    mes: str
    caminho_pdf: str
    gerado_em: date
    hash_dados: str

    def __post_init__(self):

        # Relatorio.mes: verificação e validação
        if not isinstance(self.mes, str): 
            raise TypeError(f"Relatorio.mes deve ser str ('AAAA-MM'), mas recebeu {type(self.mes).__name__}.")
        self.mes = self.mes.strip()
        try: 
            if len(self.mes) != 7: 
                raise ValueError(f"Valor inválido: Relatorio.mes não está no formato (AAAA-MM).")
            datetime.strptime(self.mes, "%Y-%m")
        except ValueError: 
            raise ValueError(f"Mês inválido: {self.mes!r}. Use o formato AAAA-MM (ex: '2026-11').")
        
        # Relatorio.caminho_pdf: verificação e validação
        if not isinstance(self.caminho_pdf, str):
            raise TypeError(f"Relatorio.caminho_pdf deve ser declarado e ser uma string.")
        self.caminho_pdf = self.caminho_pdf.strip()
        if not self.caminho_pdf:
            raise ValueError("Erro! Relatorio.caminho_pdf não pode ser vazio.")
        
        # Relatorio.gerado_em: verificação e validação
        if isinstance(self.gerado_em, str): 
            self.gerado_em = self.gerado_em.strip() # type: ignore
            try: 
                self.gerado_em = date.fromisoformat(self.gerado_em) # type: ignore
            except ValueError: raise ValueError(f"{self.gerado_em!r} não é um valor de gerado_em válido. Use o formato AAAA-MM-DD.") # type: ignore
        if type(self.gerado_em) is not date: raise TypeError(f"Tipo errôneo de dado. {type(self.gerado_em).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")
        
        # Relatorio.hash_dados: verificação e validação
        if not isinstance(self.hash_dados, str):
            raise TypeError(f"Relatorio.hash_dados deve ser declarado e ser uma string.")
        self.hash_dados = self.hash_dados.strip()
        if not self.hash_dados:
            raise ValueError("Relatorio.hash_dados não pode ficar vazio.")