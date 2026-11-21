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
        if not self.produto: raise TypeError("Meta.produto não pode ter valor vazio.")
        if isinstance(self.produto, str):
            self.produto = self.produto.strip() # type: ignore
        else: raise TypeError(f"Erro! '{self.produto}' não é uma string.")
    
        # Meta.preco_centavos
        if not self.preco_centavos: 
            raise ValueError(f"'preco_centavos' não pode ser vazio.")
        if isinstance(self.preco_centavos, str): 
            self.preco_centavos = self.preco_centavos.strip() # type: ignore
            try: 
                self.preco_centavos = int(self.preco_centavos)
                if self.preco_centavos <= 0: 
                    raise ValueError(f"{self.preco_centavos} não é um número maior que 0.")
            except (ValueError, TypeError): 
                raise TypeError(f"Erro! {self.preco_centavos} não é um número válido.")
        if not isinstance(self.preco_centavos, int): raise TypeError(f"Tipo errôneo de dado. {type(self.preco_centavos).__name__} é diferente de int ou str no formato de número.")
        
        # Meta.criada_em
        if not self.criada_em: raise TypeError(f"Erro! Meta.criada_em não pode ser vazio.")
        self.criada_em = self.criada_em.strip() # type: ignore
        if isinstance(self.criada_em, str): 
            try: 
                self.criada_em = date.fromisoformat(self.criada_em) # type: ignore
            except ValueError: raise(f"{self.criada_em!r} não é um valor de criada_em válido. Use o formato AAAA-MM-DD.") # type: ignore
        if not isinstance(self.criada_em, date): raise TypeError(f"Tipo errôneo de dado. {type(self.criada_em).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")
        
        # Meta.guardado_centavos
        if not self.guardado_centavos: 
            raise ValueError(f"'guardado_centavos' não pode ser vazio.")
        if isinstance(self.guardado_centavos, str): 
            self.guardado_centavos = self.guardado_centavos.strip() # type: ignore
            try: 
                self.guardado_centavos = int(self.guardado_centavos)
                if self.guardado_centavos <= 0: 
                    raise ValueError(f"{self.guardado_centavos} não é um número maior que 0.")
            except (ValueError, TypeError): 
                raise TypeError(f"Erro! {self.guardado_centavos} não é um número válido.")
        if not isinstance(self.guardado_centavos, int): raise TypeError(f"Tipo errôneo de dado. {type(self.guardado_centavos).__name__} é diferente de int ou str no formato de número.")
        
        # Meta.status
        if not self.status: raise ValueError(f"Meta.status deve ser definido.")
        if isinstance(self.status, str):
            self.status = self.status.strip().upper() # type: ignore
            if self.status not in ("ABERTA", "CONCLUIDA"): 
                raise ValueError(f"Tipo inválido: '{self.status}'. Use 'ABERTA' ou 'CONCLUIDA'.")
        else: raise TypeError(f"Erro! '{self.status}' não é uma string.")
        
        # Meta.concluida_em
        if self.concluida_em is not None: 
            self.concluida_em = self.concluida_em.strip() # type: ignore
            if isinstance(self.concluida_em, str): 
                try: 
                    self.concluida_em = date.fromisoformat(self.concluida_em) # type: ignore
                except ValueError: raise(f"{self.concluida_em!r} não é um valor de concluida_em válido. Use o formato AAAA-MM-DD.") # type: ignore
            if not isinstance(self.concluida_em, date): raise TypeError(f"Tipo errôneo de dado. {type(self.concluida_em).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")
        
        # Meta.prazo
        if self.prazo is not None: 
            self.prazo = self.prazo.strip() # type: ignore
            if isinstance(self.prazo, str): 
                try: 
                    self.prazo = date.fromisoformat(self.prazo) # type: ignore
                except ValueError: raise(f"{self.prazo!r} não é um valor de prazo válido. Use o formato AAAA-MM-DD.") # type: ignore
            if not isinstance(self.prazo, date): raise TypeError(f"Tipo errôneo de dado. {type(self.prazo).__name__} é diferente de date ou str no formato (AAAA-MM-DD).")
        
        # Meta.id
        if self.id is not None: 
            if isinstance(self.id, str): 
                self.id = self.id.strip() # type: ignore
                try: 
                    self.id = int(self.id) # type: ignore
                    if self.id < 1: 
                        raise ValueError(f"Valor inválido para o Meta.id: deve ser um número natural maior que 0.")
                except TypeError: 
                    raise TypeError(f"Erro! Meta.id deve ser um número inteiro.")
            if not isinstance(self.id, int): raise TypeError(f"Tipo errôneo de dado. {type(self.id).__name__} é diferente de int ou str no formato de número.")