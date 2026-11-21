from dataclasses import dataclass
from datetime import date
from typing import Literal

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

        # Transacao.tipo
        if not self.tipo: raise ValueError(f"Transacao.tipo deve ser definido.")
        if isinstance(self.tipo, str):
            self.tipo = self.tipo.strip().upper() # type: ignore
            if self.tipo not in ("ENTRADA", "SAIDA"): 
                raise ValueError(f"Tipo inválido: '{self.tipo}'. Use 'ENTRADA' ou 'SAIDA'.")
        else: raise TypeError(f"Erro! '{self.tipo}' não é uma string.")

        # Transacao.descricao
        if self.descricao is not None:
            if isinstance(self.descricao, str):
                self.descricao = self.descricao.strip() # type: ignore
            else: raise TypeError(f"Erro! '{self.descricao}' não é uma string.")

        # Transacao.valor_centavos
        if not self.valor_centavos: 
            raise ValueError(f"'valor_centavos' não pode ser vazio.")
        if isinstance(self.valor_centavos, str): 
            self.valor_centavos = self.valor_centavos.strip() # type: ignore
            try: 
                self.valor_centavos = int(self.valor_centavos)
                if self.valor_centavos <= 0: 
                    raise ValueError(f"{self.valor_centavos} não é um número maior que 0.")
            except (ValueError, TypeError): 
                raise TypeError(f"Erro! {self.valor_centavos} não é um número válido.")
        if not isinstance(self.valor_centavos, int): raise TypeError(f"Tipo errôneo de dado. {type(self.valor_centavos).__name__} é diferente de int ou str no formato de número.")

        # Transacao.data
        if not self.data: raise TypeError(f"Erro! Transacao.data não pode ser vazio.")
        self.data = self.data.strip() # type: ignore
        if isinstance(self.data, str): 
            try: 
                self.data = date.fromisoformat(self.data) # type: ignore
            except ValueError: raise(f"{self.data!r} não é um valor de data válido. Use o formato AAAA-MM-DD.") # type: ignore
        if not isinstance(self.data, date): raise TypeError(f"Tipo errôneo de dado. {type(self.data).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")

        # Transacao.categoria_id
        if not self.categoria_id: raise TypeError(f"'categoria_id' não pode ser um valor vazio.")
        self.categoria_id = self.categoria_id.strip() # type: ignore
        if isinstance(self.categoria_id, str):
            try: 
                self.categoria_id = int(self.categoria_id)
                if self.categoria_id < 1: raise ValueError(f"{self.categoria_id!r} é um valor inválido: deve ser um número natural maior que 0.")
            except: raise TypeError(f"Deve ser digitado um número para 'categoria_id'.")
        if not isinstance(self.categoria_id, int): raise TypeError(f"Tipo errôneo de dado. {type(self.categoria_id).__name__} é diferente de int ou str como número.")

        # Transacao.recorrencia_id
        if self.recorrencia_id is not None:
            self.recorrencia_id = self.recorrencia_id.strip() # type: ignore
            if isinstance(self.recorrencia_id, str):
                try: 
                    self.recorrencia_id = int(self.recorrencia_id)
                    if self.recorrencia_id < 1: raise ValueError(f"{self.recorrencia_id!r} é um valor inválido: deve ser um número natural maior que 0.")
                except: raise TypeError(f"Deve ser digitado um número para 'recorrencia_id'.")
            if not isinstance(self.recorrencia_id, int): raise TypeError(f"Tipo errôneo de dado. {type(self.recorrencia_id).__name__} é diferente de int ou str como número.")

        # Transacao.id
        if self.id is not None: 
            if isinstance(self.id, str): 
                self.id = self.id.strip() # type: ignore
                try: 
                    self.id = int(self.id) # type: ignore
                    if self.id < 1: 
                        raise ValueError(f"Valor inválido para o Transacao.id: deve ser um número natural maior que 0.")
                except TypeError: 
                    raise TypeError(f"Erro! Transacao.id deve ser um número inteiro.")
            if not isinstance(self.id, int): raise TypeError(f"Tipo errôneo de dado. {type(self.id).__name__} é diferente de int ou str no formato de número.")