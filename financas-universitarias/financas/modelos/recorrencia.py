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
                try:
                    self.id = int(self.id.strip())
                except ValueError:
                    raise ValueError(f"'{self.id}' não é um inteiro válido para id.")
            elif isinstance(self.id, bool) or not isinstance(self.id, int): 
                raise TypeError(f"'{self.id}' não corresponde a um número inteiro.")
            if self.id < 1: 
                raise ValueError("Recorrencia.id deve ser um número inteiro maior que 0.")

        # Recorrencia.tipo
        if not isinstance(self.tipo, str):
            raise TypeError("Recorrencia.tipo deve existir e ser do tipo 'str'.")
        self.tipo = self.tipo.strip().upper() # type: ignore
        if self.tipo not in ("ENTRADA", "SAIDA"): 
            raise ValueError(f"Tipo inválido: '{self.tipo}'. Use 'ENTRADA' ou 'SAIDA'.")

        # Recorrencia.descricao
        if self.descricao is not None:
            if isinstance(self.descricao, str):
                self.descricao = self.descricao.strip() or None # type: ignore
            else: raise TypeError(f"Erro! '{self.descricao}' não é uma string.")

        # Recorrencia.periodicidade
        if not isinstance(self.periodicidade, str):
            raise TypeError("Recorrencia.periodicidade deve existir e ser do tipo 'str'.")
        self.periodicidade = self.periodicidade.strip().upper() # type: ignore
        if self.periodicidade not in ("SEMANAL", "MENSAL"): 
            raise ValueError(f"{self.periodicidade} não é válido. Tente 'SEMANAL' ou 'MENSAL'.")

        # Recorrencia.dia
        if isinstance(self.dia, str): 
            try: 
                self.dia = int(self.dia.strip())
            except ValueError: 
                raise ValueError(f"'{self.dia}' não é um número inteiro válido")
        if isinstance(self.dia, bool) or not isinstance(self.dia, int): raise TypeError(f"Tipo errôneo de dado. {type(self.dia).__name__} é diferente de int ou str no formato de número.")
        if self.periodicidade == "MENSAL" and not (1 <= self.dia <= 31): 
            raise ValueError(f"Para periodicidade {self.periodicidade}, o valor deve estar no intervalo de 1 a 31 em 'Recorrencia.dia'.")
        elif self.periodicidade == "SEMANAL" and not (1 <= self.dia <= 7):
            raise ValueError(f"Para periodicidade {self.periodicidade}, o valor deve estar no intervalo de 1 a 7 em 'Recorrencia.dia'.")

        # Recorrencia.valor_centavos
        if isinstance(self.valor_centavos, str): 
            try:
                self.valor_centavos = int(self.valor_centavos.strip())
            except ValueError:
                raise ValueError(f"'{self.valor_centavos}' não é um inteiro válido para valor_centavos.")
        elif isinstance(self.valor_centavos, bool) or not isinstance(self.valor_centavos, int): 
            raise TypeError(f"'{self.valor_centavos}' não corresponde a um número inteiro.")
        if self.valor_centavos <= 0: 
            raise ValueError("Recorrencia.valor_centavos deve ser um número inteiro maior que 0.")

        # Recorrencia.data_inicio
        if isinstance(self.data_inicio, str): 
            self.data_inicio = self.data_inicio.strip() # type: ignore
            try: 
                self.data_inicio = date.fromisoformat(self.data_inicio) # type: ignore
            except ValueError: raise ValueError(f"{self.data_inicio!r} não é um valor de data válido. Use o formato AAAA-MM-DD.") # type: ignore
        if type(self.data_inicio) is not date: raise TypeError(f"Tipo errôneo de dado. {type(self.data_inicio).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")

        # Recorrencia.data_fim
        if self.data_fim is not None: 
            if isinstance(self.data_fim, str): 
                self.data_fim = self.data_fim.strip() # type: ignore
                try: 
                    self.data_fim = date.fromisoformat(self.data_fim) # type: ignore
                except ValueError: raise ValueError(f"{self.data_fim!r} não é um valor de data válido. Use o formato AAAA-MM-DD.") # type: ignore
            if type(self.data_fim) is not date:
                raise TypeError(f"Tipo errôneo de dado. {type(self.data_fim).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")
            if self.data_fim < self.data_inicio: 
                raise ValueError(f"Recorrencia.data_fim ({self.data_fim}) não pode ser uma data anterior a Recorrencia.data_inicio ({self.data_inicio}).")

        # Recorrencia.categoria_id
        if isinstance(self.categoria_id, str): 
            try:
                self.categoria_id = int(self.categoria_id.strip())
            except ValueError:
                raise ValueError(f"'{self.categoria_id}' não é um inteiro válido para categoria_id.")
        elif isinstance(self.categoria_id, bool) or not isinstance(self.categoria_id, int): 
            raise TypeError(f"'{self.categoria_id}' não corresponde a um número inteiro.")
        if self.categoria_id < 1: 
            raise ValueError("Recorrencia.categoria_id deve ser um número inteiro maior que 0.")