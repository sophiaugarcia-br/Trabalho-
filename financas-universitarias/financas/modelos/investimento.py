from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import Literal

@dataclass
class Investimento: 
    nome: str
    valor_inicial_centavos: int
    taxa: Decimal
    periodicidade_taxa: Literal["AA", "AM"]
    data_inicio: date
    data_resgate: date | None = None
    id: int | None = None

    def __post_init__(self):

        # Investimento.nome
        if not self.nome: raise TypeError("Investimento.nome não pode ter valor vazio.")
        if isinstance(self.nome, str):
            self.nome = self.nome.strip() # type: ignore
        else: raise TypeError(f"Erro! '{self.nome}' não é uma string.")

        # Investimento.valor_inicial_centavos
        if not self.valor_inicial_centavos: 
            raise ValueError(f"'valor_inicial_centavos' não pode ser vazio.")
        if isinstance(self.valor_inicial_centavos, str): 
            self.valor_inicial_centavos = self.valor_inicial_centavos.strip() # type: ignore
            try: 
                self.valor_inicial_centavos = int(self.valor_inicial_centavos)
                if self.valor_inicial_centavos <= 0: 
                    raise ValueError(f"{self.valor_inicial_centavos} não é um número maior que 0.")
            except (ValueError, TypeError): 
                raise TypeError(f"Erro! {self.valor_inicial_centavos} não é um número válido.")
        if not isinstance(self.valor_inicial_centavos, int): raise TypeError(f"Tipo errôneo de dado. {type(self.valor_inicial_centavos).__name__} é diferente de int ou str no formato de número.")

        # Investimento.taxa
        if not self.taxa: 
            raise ValueError(f"'taxa' não pode ser vazio.")
        if isinstance(self.taxa, str): 
            self.taxa = self.taxa.strip() # type: ignore
            try: 
                self.taxa = Decimal(self.taxa)
            except (ValueError, TypeError): 
                raise TypeError(f"Erro! {self.taxa} não é um número real.")
        if not isinstance(self.taxa, Decimal): raise TypeError(f"Tipo errôneo de dado. {type(self.taxa).__name__} é diferente de decimal ou str no formato de número.")

        # Investimento.periodicidade_taxa
        

        # Investimento.data_inicio


        # Investimento.data_resgate


        # Investimento.id

