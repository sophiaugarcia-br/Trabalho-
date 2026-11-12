
from financas.utils.validacao import (
    validar_obrigatorio, validar_valor, validar_data, validar_lancamento
)

def test_obrigatorio():
    assert validar_obrigatorio("Mercado", "Descrição") == []
    assert validar_obrigatorio("", "Descrição") == ["Descrição é obrigatório."]
    assert validar_obrigatorio("   ", "Descrição") != []
    assert validar_obrigatorio(None, "Descrição") != []

def test_valor():
    assert validar_valor("12,50") == []
    assert validar_valor("0") == ["Valor deve ser maior que zero."]
    assert validar_valor("-5") != []
    assert validar_valor("abc") == ["Valor inválido."]
    assert validar_valor("") != []

def test_data():
    assert validar_data("2026-11-12") == []
    assert validar_data("2026-02-30") != []
    assert validar_data("12/11/2026") != []
    assert validar_data(None) != []

def test_lancamento_valido():
    dados = {"tipo": "SAIDA", "descricao": "Almoço", "valor": "25,90",
             "data": "2026-11-12", "categoria_id": "1"}
    assert validar_lancamento(dados) == []

def test_lancamento_varios_erros():
    dados = {"tipo": "OUTRO", "descricao": "", "valor": "0",
             "data": "2026-13-01", "categoria_id": ""}
    assert len(validar_lancamento(dados)) == 5
