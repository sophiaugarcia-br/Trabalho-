from dataclasses import dataclass
from datetime import date
from typing import Literal

@dataclass
class Meta: 
    produto: str
    preco_centavos: int
    criada_em: date
    guardado_centavos: int
    status: Literal["ABERTA", "CONCLUIDA"]
    concluida_em: date | None = None
    prazo: date | None = None
    id: int | None = None

    def __post_init__(self):

        # Meta.produto
        if not isinstance(self.produto, str):
            raise TypeError(f"Meta.produto deve ser declarado e ser uma string.")
        self.produto = self.produto.strip()
        if not self.produto:
            raise ValueError("Meta.produto não pode ficar vazio.")

        # Meta.preco_centavos
        if isinstance(self.preco_centavos, str): 
            try:
                self.preco_centavos = int(self.preco_centavos.strip())
            except ValueError:
                raise ValueError(f"'{self.preco_centavos}' não é um inteiro válido para preco_centavos.")
        elif isinstance(self.preco_centavos, bool) or not isinstance(self.preco_centavos, int): 
            raise TypeError(f"'{self.preco_centavos}' não corresponde a um número inteiro.")
        if self.preco_centavos <= 0: 
            raise ValueError("Meta.preco_centavos deve ser um número inteiro maior que 0.")

        # Meta.criada_em
        if isinstance(self.criada_em, str): 
            self.criada_em = self.criada_em.strip() # type: ignore
            try: 
                self.criada_em = date.fromisoformat(self.criada_em) # type: ignore
            except ValueError: raise ValueError(f"{self.criada_em!r} não é um valor de criada_em válido. Use o formato AAAA-MM-DD.") # type: ignore
        if type(self.criada_em) is not date: raise TypeError(f"Tipo errôneo de dado. {type(self.criada_em).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")

        # Meta.guardado_centavos
        if isinstance(self.guardado_centavos, str): 
            try:
                self.guardado_centavos = int(self.guardado_centavos.strip())
            except ValueError:
                raise ValueError(f"'{self.guardado_centavos}' não é um inteiro válido para guardado_centavos.")
        elif isinstance(self.guardado_centavos, bool) or not isinstance(self.guardado_centavos, int): 
            raise TypeError(f"'{self.guardado_centavos}' não corresponde a um número inteiro.")
        if self.guardado_centavos < 0: 
            raise ValueError("Meta.guardado_centavos deve ser um número inteiro maior ou igual a 0.")

        # Meta.status
        if not isinstance(self.status, str):
            raise TypeError("Meta.status deve existir e ser do tipo 'str'.")
        self.status = self.status.strip().upper() # type: ignore
        if self.status not in ("ABERTA", "CONCLUIDA"): 
            raise ValueError(f"Tipo inválido: '{self.status}'. Use 'ABERTA', 'CONCLUIDA'.")
        if self.status == "CONCLUIDA" and self.concluida_em is None: raise ValueError(f"Valor inválido: Meta.status ({self.status}) não condiz com Meta.concluida_em ({self.concluida_em})! Meta.concluida_em deve ser declarada uma vez que Meta.status = 'CONCLUIDA'.")
        if self.status == "ABERTA" and self.concluida_em is not None: raise ValueError("Meta.concluida_em deve ser None enquanto Meta.status for 'ABERTA'.")

        # Meta.concluida_em
        if self.concluida_em is not None: 
            if isinstance(self.concluida_em, str): 
                self.concluida_em = self.concluida_em.strip() # type: ignore
                try: 
                    self.concluida_em = date.fromisoformat(self.concluida_em) # type: ignore
                except ValueError: raise ValueError(f"{self.concluida_em!r} não é um valor de concluida_em válido. Use o formato AAAA-MM-DD.") # type: ignore
            if type(self.concluida_em) is not date: raise TypeError(f"Tipo errôneo de dado. {type(self.concluida_em).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")
            if self.concluida_em < self.criada_em: 
                raise ValueError(f"Valor inválido: Meta.concluida_em ({self.concluida_em}) é anterior a Meta.criada_em ({self.criada_em})!")

        # Meta.prazo
        if self.prazo is not None: 
            if isinstance(self.prazo, str): 
                self.prazo = self.prazo.strip() # type: ignore
                try: 
                    self.prazo = date.fromisoformat(self.prazo) # type: ignore
                except ValueError: raise ValueError(f"{self.prazo!r} não é um valor de prazo válido. Use o formato AAAA-MM-DD.") # type: ignore
            if type(self.prazo) is not date: raise TypeError(f"Tipo errôneo de dado. {type(self.prazo).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")

        # Meta.id
        if self.id is not None: 
            if isinstance(self.id, str): 
                try:
                    self.id = int(self.id.strip())
                except ValueError:
                    raise ValueError(f"'{self.id}' não é um inteiro válido para id.")
            elif isinstance(self.id, bool) or not isinstance(self.id, int): 
                raise TypeError(f"Tipo errôneo de dado. '{type(self.id).__name__}' é diferente de int.")
            if self.id < 1: 
                raise ValueError("Valor inválido para o Meta.id: deve ser um número inteiro maior que 0.")