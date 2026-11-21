from dataclasses import dataclass
from datetime import date
from typing import Literal

@dataclass
class Categoria: 
    nome: str
    tipo: Literal["ENTRADA", "SAIDA"]
    cor: str = "#FFFFFF"
    id: int | None = None

    def __post_init__(self):

        # Categoria.tipo
        if not self.tipo: raise ValueError(f"Recorrencia.tipo deve ser definido.")
        if isinstance(self.tipo, str):
            self.tipo = self.tipo.strip().upper() # type: ignore
            if self.tipo not in ("ENTRADA", "SAIDA"): 
                raise ValueError(f"Tipo inválido: '{self.tipo}'. Use 'ENTRADA' ou 'SAIDA'.")
        else: raise TypeError(f"Erro! '{self.tipo}' não é uma string.")

        # Categoria.nome
        if not self.nome: raise TypeError("Categoria.nome não pode ter valor vazio.")
        if isinstance(self.nome, str):
            self.nome = self.nome.strip() # type: ignore
        else: raise TypeError(f"Erro! '{self.nome}' não é uma string.")

        # Categoria.cor
        if not self.cor: raise TypeError("Categoria.cor não pode ter valor vazio.")
        if isinstance(self.cor, str):
            self.cor = self.cor.strip().upper() # type: ignore
            if not self.cor[0] == "#" or not len(self.cor) == 7:
                raise ValueError(f"'{self.cor}' não corresponde a uma cor rgb em hexadecimal (ex. #FFFFFF).")
        else: raise TypeError(f"Erro! '{self.cor}' não é uma string.")

        # Categoria.id
        if self.id is not None: 
            if isinstance(self.id, str): 
                self.id = self.id.strip() # type: ignore
                try: 
                    self.id = int(self.id) # type: ignore
                    if self.id < 1: 
                        raise ValueError(f"Valor inválido para o Categoria.id: deve ser um número natural maior que 0.")
                except TypeError: 
                    raise TypeError(f"Erro! Categoria.id deve ser um número inteiro.")
            if not isinstance(self.id, int): raise TypeError(f"Tipo errôneo de dado. {type(self.id).__name__} é diferente de int ou str no formato de número.")