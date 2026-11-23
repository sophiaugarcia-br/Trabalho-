from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
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
        if not isinstance(self.nome, str):
            raise TypeError(f"Investimento.nome deve ser declarado e ser uma string.")
        self.nome = self.nome.strip()
        if not self.nome:
            raise ValueError("Investimento.nome não pode ficar vazio.")

        # Investimento.valor_inicial_centavos
        if isinstance(self.valor_inicial_centavos, str): 
            try:
                self.valor_inicial_centavos = int(self.valor_inicial_centavos.strip())
            except ValueError:
                raise ValueError(f"'{self.valor_inicial_centavos}' não é um inteiro válido para valor_inicial_centavos.")
        elif isinstance(self.valor_inicial_centavos, bool) or not isinstance(self.valor_inicial_centavos, int): 
            raise TypeError(f"'{self.valor_inicial_centavos}' não corresponde a um número inteiro.")
        if self.valor_inicial_centavos <= 0: 
            raise ValueError("Investimento.valor_inicial_centavos deve ser um número inteiro maior que 0.")

        # Investimento.taxa
        if isinstance(self.taxa, (str, float)): 
            try: 
                self.taxa = Decimal(str(self.taxa).strip())
            except InvalidOperation: 
                raise ValueError(f"'{self.taxa}' não é um valor decimal.")
        elif not isinstance(self.taxa, bool) and isinstance(self.taxa, int): 
            self.taxa = Decimal(self.taxa)
        if not isinstance(self.taxa, Decimal): 
            raise TypeError("Investimento.taxa não é um tipo de dado válido para valores em decimal.")
        if not self.taxa.is_finite(): raise ValueError("Investimento.taxa deve ser um número finito.")
        if self.taxa < 0: 
            raise ValueError(f"'{self.taxa}' não pode ser negativo.")

        # Investimento.periodicidade_taxa
        if not isinstance(self.periodicidade_taxa, str):
            raise TypeError("Investimento.periodicidade_taxa deve ser definido e ser do tipo 'str'.")
        self.periodicidade_taxa = self.periodicidade_taxa.strip().upper() # type: ignore
        if self.periodicidade_taxa not in ("AA", "AM"): 
            raise ValueError(f"Tipo inválido: '{self.periodicidade_taxa}'. Use 'AA' (ao ano) ou 'AM' (ao mês).")

        # Investimento.data_inicio
        if isinstance(self.data_inicio, str): 
            self.data_inicio = self.data_inicio.strip() # type: ignore
            try: 
                self.data_inicio = date.fromisoformat(self.data_inicio) # type: ignore
            except ValueError: raise ValueError(f"{self.data_inicio!r} não é um valor de data válido. Use o formato AAAA-MM-DD.") # type: ignore
        if type(self.data_inicio) is not date: raise TypeError(f"Tipo errôneo de dado. {type(self.data_inicio).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")

        # Investimento.data_resgate
        if self.data_resgate is not None: 
            if isinstance(self.data_resgate, str): 
                self.data_resgate = self.data_resgate.strip() # type: ignore
                try: 
                    self.data_resgate = date.fromisoformat(self.data_resgate) # type: ignore
                except ValueError: raise ValueError(f"{self.data_resgate!r} não é um valor de data válido. Use o formato AAAA-MM-DD.") # type: ignore
            if type(self.data_resgate) is not date:
                raise TypeError(f"Tipo errôneo de dado. {type(self.data_resgate).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")
            if self.data_resgate < self.data_inicio: 
                raise ValueError(f"Investimento.data_resgate ({self.data_resgate}) não pode ser uma data anterior a Investimento.data_inicio ({self.data_inicio}).")

        # Investimento.id
        if self.id is not None: 
            if isinstance(self.id, str): 
                try:
                    self.id = int(self.id.strip())
                except ValueError:
                    raise ValueError(f"'{self.id}' não é um inteiro válido para id.")
            elif isinstance(self.id, bool) or not isinstance(self.id, int): 
                raise TypeError(f"'{self.id}' não corresponde a um número inteiro.")
            if self.id < 1: 
                raise ValueError("Investimento.id deve ser um número inteiro maior que 0.")