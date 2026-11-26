from dataclasses import dataclass
from datetime import date
from typing import Literal

"""  Este arquivo cria a classe (molde) 'Transacao' para todo dado (objeto) que é uma transacao, cuja qual tem um tipo, valor_centavos, data, categoria_id, descricao, recorrencia_id, id (ex: 'SAIDA', 24390, 2023-01-03, 1, None, 4, 5). Isso serve para definir e aceitar universalmente, em variáveis daquele transacao, apenas um tipo de dado por atributo.  """

@dataclass
class Transacao: 
    tipo: Literal["ENTRADA", "SAIDA"]
    valor_centavos: int
    data: date
    categoria_id: int
    descricao: str | None = None
    recorrencia_id: int | None = None
    id: int | None = None

    def __post_init__(self):

        # Transacao.tipo: verificação e validação
        if not isinstance(self.tipo, str):
            raise TypeError("Transacao.tipo deve existir e ser do tipo 'str'.")
        self.tipo = self.tipo.strip().upper() # type: ignore
        if self.tipo not in ("ENTRADA", "SAIDA"): 
            raise ValueError(f"Tipo inválido: '{self.tipo}'. Use 'ENTRADA' ou 'SAIDA'.")

        # Transacao.descricao: verificação e validação
        if self.descricao is not None:
            if isinstance(self.descricao, str):
                self.descricao = self.descricao.strip() or None # type: ignore
            else: raise TypeError(f"Erro! '{self.descricao}' não é uma string.")

        # Transacao.valor_centavos: verificação e validação
        if isinstance(self.valor_centavos, str): 
            try:
                self.valor_centavos = int(self.valor_centavos.strip())
            except ValueError:
                raise ValueError(f"'{self.valor_centavos}' não é um inteiro válido para valor_centavos.")
        elif isinstance(self.valor_centavos, bool) or not isinstance(self.valor_centavos, int): 
            raise TypeError(f"'{self.valor_centavos}' não corresponde a um número inteiro.")
        if self.valor_centavos <= 0: 
            raise ValueError("Transacao.valor_centavos deve ser um número inteiro maior que 0.")

        # Transacao.data: verificação e validação
        if isinstance(self.data, str): 
            self.data = self.data.strip() # type: ignore
            try: 
                self.data = date.fromisoformat(self.data) # type: ignore
            except ValueError: raise ValueError(f"{self.data!r} não é um valor de data válido. Use o formato AAAA-MM-DD.") # type: ignore
        if type(self.data) is not date: raise TypeError(f"Tipo errôneo de dado. {type(self.data).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")

        # Transacao.categoria_id: verificação e validação
        if isinstance(self.categoria_id, str): 
            try:
                self.categoria_id = int(self.categoria_id.strip())
            except ValueError:
                raise ValueError(f"'{self.categoria_id}' não é um inteiro válido para categoria_id.")
        elif isinstance(self.categoria_id, bool) or not isinstance(self.categoria_id, int): 
            raise TypeError(f"'{self.categoria_id}' não corresponde a um número inteiro.")
        if self.categoria_id < 1: 
            raise ValueError("Transacao.categoria_id deve ser um número inteiro maior que 0.")

        # Transacao.recorrencia_id: verificação e validação
        if self.recorrencia_id is not None:
            if isinstance(self.recorrencia_id, str): 
                try:
                    self.recorrencia_id = int(self.recorrencia_id.strip())
                except ValueError:
                    raise ValueError(f"'{self.recorrencia_id}' não é um inteiro válido para recorrencia_id.")
            elif isinstance(self.recorrencia_id, bool) or not isinstance(self.recorrencia_id, int): 
                raise TypeError(f"'{self.recorrencia_id}' não corresponde a um número inteiro.")
            if self.recorrencia_id < 1: 
                raise ValueError("Transacao.recorrencia_id deve ser um número inteiro maior que 0.")

        # Transacao.id: verificação e validação
        if self.id is not None: 
            if isinstance(self.id, str): 
                try:
                    self.id = int(self.id.strip())
                except ValueError:
                    raise ValueError(f"'{self.id}' não é um inteiro válido para id.")
            elif isinstance(self.id, bool) or not isinstance(self.id, int): 
                raise TypeError(f"'{self.id}' não corresponde a um número inteiro.")
            if self.id < 1: 
                raise ValueError("Transacao.id deve ser um número inteiro maior que 0.")