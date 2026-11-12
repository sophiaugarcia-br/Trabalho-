

import pytest
from financas.utils.dinheiro import centavos, formatar_brl, dividir_centavos

def test_centavos():
    assert para_centavos("12.50") == 1250
    assert para_centavos("1.250,00") == 125000
    assert para_centavos("R$ 3,00") == 300
    
def teste_arredodndamento():
    assert para_centavos("12,505") == 1251

def teste_valor_invalido():
    with pytest.raises(ValueError):
        para_centavos("abc")
    with pytest.raises(ValueError):
        para_centavos("")
        
def teste_formatar_brl():
    assert formatar_brl(1250) == "R$ 12,50"
    assert formatar_brl(125000) == "R$ 1250,00"
    assert formatar_brl(5) == "R$ 0,05"
    assert formatar_brl(0) == "R$ 0,00"
    assert formatar_brl(-1250) == "-R$ 12,50"

def test_dividir_centavos():
    assert dividir_centavos(120000, 26) == 4615   # 46,15
    assert dividir_centavos(120000, 6) == 20000   # exato
    assert dividir_centavos(10, 4) == 3           # 2,5 arredonda para 3
    assert dividir_centavos(0, 5) == 0
