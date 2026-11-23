from dataclasses import dataclass
from datetime import date
from typing import Literal

@dataclass
class Previsao: 
    gerada_em: date
    saldo_projetado_centavos: int
    situacao: Literal["LUCRO", "EQUILIBRIO", "DIVIDA"]
    id: int | None = None

    def __post_init__(self):

        # Previsao.gerada_em
        if isinstance(self.gerada_em, str): 
            self.gerada_em = self.gerada_em.strip() # type: ignore
            try: 
                self.gerada_em = date.fromisoformat(self.gerada_em) # type: ignore
            except ValueError: raise ValueError(f"{self.gerada_em!r} não é um valor de gerada_em válido. Use o formato AAAA-MM-DD.") # type: ignore
        if type(self.gerada_em) is not date: raise TypeError(f"Tipo errôneo de dado. {type(self.gerada_em).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")

        # Previsao.saldo_projetado_centavos
        if isinstance(self.saldo_projetado_centavos, str): 
            try:
                self.saldo_projetado_centavos = int(self.saldo_projetado_centavos.strip())
            except ValueError:
                raise ValueError(f"'{self.saldo_projetado_centavos}' não é um inteiro válido para saldo_projetado_centavos.")
        elif isinstance(self.saldo_projetado_centavos, bool) or not isinstance(self.saldo_projetado_centavos, int): 
            raise TypeError(f"'{self.saldo_projetado_centavos}' não corresponde a um número inteiro.")

        # Previsao.situacao
        if not isinstance(self.situacao, str):
            raise TypeError("Previsao.situacao deve ser definido e ser do tipo 'str'.")
        self.situacao = self.situacao.strip().upper() # type: ignore
        if self.situacao not in ("LUCRO", "EQUILIBRIO", "DIVIDA"): 
            raise ValueError(f"Tipo inválido: '{self.situacao}'. Use 'LUCRO', 'EQUILIBRIO' ou 'DIVIDA'.")
        if self.situacao == "LUCRO" and self.saldo_projetado_centavos <= 0: 
            raise ValueError(f"Erro! A situação '{self.situacao}' não corresponde a Previsao.saldo_projetado_centavos ({self.saldo_projetado_centavos}).")
        elif self.situacao == "EQUILIBRIO" and self.saldo_projetado_centavos != 0: 
            raise ValueError(f"Erro! A situação '{self.situacao}' não corresponde a Previsao.saldo_projetado_centavos ({self.saldo_projetado_centavos}).")
        elif self.situacao == "DIVIDA" and self.saldo_projetado_centavos >= 0: 
            raise ValueError(f"Erro! A situação '{self.situacao}' não corresponde a Previsao.saldo_projetado_centavos ({self.saldo_projetado_centavos}).")

        # Previsao.id
        if self.id is not None: 
            if isinstance(self.id, str): 
                try:
                    self.id = int(self.id.strip())
                except ValueError:
                    raise ValueError(f"'{self.id}' não é um inteiro válido para id.")
            elif isinstance(self.id, bool) or not isinstance(self.id, int): 
                raise TypeError(f"Erro! Previsao.id deve ser um número inteiro.")
            if self.id < 1: 
                raise ValueError("Previsao.id deve ser um número inteiro maior que 0.")