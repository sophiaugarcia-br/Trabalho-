

import pytest
from financas.utils.dinheiro import centavos, formatar_brl

def test_centavos():
    assert centavos("12.50") == 1250
    assert centavos("1.250,00") == 125000
    assert centavos("R$ 3,00") == 300
    
def teste_arredodndamento():
    assert centavos("12,505") == 1251

def teste_valor_invalido():
    with pytest.raises(ValueError):
        centavos("abc")
    with pytest.raises(ValueError):
        centavos("")
        
def teste_formatar_brl():
    assert formatar_brl(1250) == "R$ 12,50"
    assert formatar_brl(125000) == "R$ 1250,00"
    assert formatar_brl(5) == "R$ 0,05"
    assert formatar_brl(0) == "R$ 0,00"
    assert formatar_brl(-1250) == "-R$ 12,50"
