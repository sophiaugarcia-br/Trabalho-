from dataclasses import dataclass
from datetime import date
from typing import Literal

@dataclass
class Recorrencia: 
    tipo: Literal["ENTRADA", "SAIDA"]
    valor_centavos: int
    periodicidade: Literal["SEMANAL", "MENSAL"]
    dia: int
    data_inicio: date
    categoria_id: int
    descricao: str | None = None
    data_fim: date | None = None
    id: int | None = None

    def __post_init__(self): 

        # Recorrencia.id
        if self.id is not None: 
            if isinstance(self.id, str): 
                self.id = self.id.strip() # type: ignore
                try: 
                    self.id = int(self.id) # type: ignore
                    if self.id < 1: 
                        raise ValueError(f"Valor inválido para o Recorrencia.id: deve ser um número natural maior que 0.")
                except TypeError: 
                    raise TypeError(f"Erro! Recorrencia.id deve ser um número inteiro.")
            if not isinstance(self.id, int): raise TypeError(f"Tipo errôneo de dado. {type(self.id).__name__} é diferente de int ou str no formato de número.")

        # Recorrencia.tipo
        if not self.tipo: raise ValueError(f"Recorrencia.tipo deve ser definido.")
        if isinstance(self.tipo, str):
            self.tipo = self.tipo.strip().upper() # type: ignore
            if self.tipo not in ("ENTRADA", "SAIDA"): 
                raise ValueError(f"Tipo inválido: '{self.tipo}'. Use 'ENTRADA' ou 'SAIDA'.")
        else: raise TypeError(f"Erro! '{self.tipo}' não é uma string.")

        # Recorrencia.descricao
        if self.descricao is not None:
            if isinstance(self.descricao, str):
                self.descricao = self.descricao.strip() # type: ignore
            else: raise TypeError(f"Erro! '{self.descricao}' não é uma string.")

        # Recorrencia.periodicidade
        if not self.periodicidade: raise ValueError(f"O valor de periodicidade não pode ser vazio.")
        if isinstance(self.periodicidade, str): 
            self.periodicidade = self.periodicidade.strip().upper() # type: ignore
            if self.periodicidade not in ("SEMANAL", "MENSAL"): 
                raise ValueError(f"{self.periodicidade} não é válido. Tente 'SEMANAL' ou 'MENSAL'.")
        else: raise TypeError(f"Recorrencia.periodicidade deve ser do tipo texto.")

        # Recorrencia.dia
        if not self.dia: raise ValueError(f"O valor de dia não pode ser vazio.")
        if isinstance(self.dia, str): 
            try: 
                self.dia = int(self.dia)
                if self.periodicidade == "MENSAL" and not (1 <= self.dia <= 31): 
                    raise ValueError(f"Para periodicidade {self.periodicidade}, o valor deve estar no intervalo de 1 a 31 em 'Recorrencia.dia'.")
                elif not (1 <= self.dia <= 7): 
                    raise ValueError(f"Para periodicidade {self.periodicidade}, o valor deve estar no intervalo de 1 a 7 em 'Recorrencia.dia'.")
            except (TypeError, ValueError): 
                raise ValueError(f"'{self.dia}' não é um número inteiro válido")
        if not isinstance(self.dia, int): raise TypeError(f"Tipo errôneo de dado. {type(self.dia).__name__} é diferente de int ou str no formato de número.")

        # Recorrencia.valor_centavos
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

        # Recorrencia.data_inicio
        if not self.data_inicio: raise TypeError(f"Erro! Recorrencia.data_inicio não pode ser vazio.")
        self.data_inicio = self.data_inicio.strip() # type: ignore
        if isinstance(self.data_inicio, str): 
            try: 
                self.data_inicio = date.fromisoformat(self.data_inicio) # type: ignore
            except ValueError: raise(f"{self.data_inicio!r} não é um valor de data válido. Use o formato AAAA-MM-DD.") # type: ignore
        if not isinstance(self.data_inicio, date): raise TypeError(f"Tipo errôneo de dado. {type(self.data_inicio).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")

        # Recorrencia.data_fim
        if self.data_fim is not None: 
            if isinstance(self.data_fim, str): 
                self.data_fim = self.data_fim.strip() # type: ignore
                try: 
                    self.data_fim = date.fromisoformat(self.data_fim) # type: ignore
                except ValueError: raise(f"{self.data_fim!r} não é um valor de data válido. Use o formato AAAA-MM-DD.") # type: ignore
            if not isinstance(self.data_fim, date): 
                raise TypeError(f"Tipo errôneo de dado. {type(self.data_fim).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")

        # Recorrencia.categoria_id
        if not self.categoria_id: raise TypeError(f"'categoria_id' não pode ser um valor vazio.")
        self.categoria_id = self.categoria_id.strip() # type: ignore
        if isinstance(self.categoria_id, str):
            try: 
                self.categoria_id = int(self.categoria_id)
                if self.categoria_id < 1: raise ValueError(f"{self.categoria_id!r} é um valor inválido: deve ser um número natural maior que 0.")
            except: raise TypeError(f"Deve ser digitado um número para 'categoria_id'.")
        if not isinstance(self.categoria_id, int): raise TypeError(f"Tipo errôneo de dado. {type(self.categoria_id).__name__} é diferente de int ou str como número.")