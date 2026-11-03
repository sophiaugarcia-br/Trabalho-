
from financas.utils.dinheiro import para_centavos, formatar_brl

def test_para_centavos():
    assert para_centavos("12,50") == 1250
    assert para_centavos("R$ 1.234,56") == 123456
    assert para_centavos("10") == 1000

def test_formatar_brl():
    assert formatar_brl(1250) == "R$ 12,50"
    assert formatar_brl(123456) == "R$ 1.234,56"
    assert formatar_brl(5) == "R$ 0,05"
    assert formatar_brl(-1250) == "-R$ 12,50"
