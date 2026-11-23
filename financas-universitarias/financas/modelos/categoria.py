from dataclasses import dataclass
from typing import Literal

@dataclass
class Categoria: 
    nome: str
    tipo: Literal["ENTRADA", "SAIDA"]
    cor: str = "#FFFFFF"
    id: int | None = None

    def __post_init__(self):

        # Categoria.tipo
        if not isinstance(self.tipo, str):
            raise TypeError("Categoria.tipo deve existir e ser do tipo 'str'.")
        self.tipo = self.tipo.strip().upper() # type: ignore
        if self.tipo not in ("ENTRADA", "SAIDA"): 
            raise ValueError(f"Tipo inválido: '{self.tipo}'. Use 'ENTRADA' ou 'SAIDA'.")

        # Categoria.nome
        if not isinstance(self.nome, str):
            raise TypeError(f"Categoria.nome deve ser declarado e ser uma string.")
        self.nome = self.nome.strip()
        if not self.nome:
            raise ValueError("Categoria.nome não pode ficar vazio.")

        # Categoria.cor
        if not isinstance(self.cor, str):
            raise TypeError(f"Categoria.cor não pode ter valor vazio e deve ser string.")
        self.cor = self.cor.strip().upper()
        if len(self.cor) != 7 or not self.cor[0] == "#":
            raise ValueError(f"'{self.cor}' não corresponde a uma cor rgb em hexadecimal (ex. '#FFFFFF').")
        for caractere in self.cor[1:]: 
            if caractere not in ('0123456789ABCDEF'): 
                raise ValueError(f"'{self.cor}' não corresponde a uma cor rgb em hexadecimal (ex. '#FFFFFF').")

        # Categoria.id
        if self.id is not None: 
            if isinstance(self.id, str): 
                try:
                    self.id = int(self.id.strip())
                except ValueError:
                    raise ValueError(f"'{self.id}' não é um inteiro válido para id.")
            elif isinstance(self.id, bool) or not isinstance(self.id, int): 
                raise TypeError(f"'{self.id}' não corresponde a um número inteiro.")
            if self.id < 1: 
                raise ValueError("Categoria.id deve ser um número inteiro maior que 0.")