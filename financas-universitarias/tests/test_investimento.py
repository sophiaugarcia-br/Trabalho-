
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
import pytest
from financas.servicos.investimento_service import (
    taxa_anual, montante, ativo_no_mes, rendimento_no_mes, resumo_mes
)
from financas.utils.dinheiro import arredondar_centavos

def inv(valor=100000, taxa="0.12", per="AA",
        inicio=date(2026, 1, 1), resgate=None):
    return SimpleNamespace(nome="CDB", valor_inicial_centavos=valor,
                           taxa=taxa, periodicidade_taxa=per,
                           data_inicio=inicio, data_resgate=resgate)

def test_exemplo_da_especificacao():
    assert arredondar_centavos(montante(inv(), date(2027, 1, 1))) == 112000

def test_taxa_mensal_vira_anual():
    t = taxa_anual(inv(taxa="0.01", per="AM"))
    assert abs(t - Decimal("0.1268250301")) < Decimal("0.0000000001")
    assert taxa_anual(inv()) == Decimal("0.12")

def test_periodicidade_invalida():
    with pytest.raises(ValueError):
        taxa_anual(inv(per="XX"))

def test_ativo_no_mes():
    assert ativo_no_mes(inv(inicio=date(2026, 11, 30)), 2026, 11)
    assert not ativo_no_mes(inv(inicio=date(2026, 12, 1)), 2026, 11)
    assert ativo_no_mes(inv(resgate=date(2026, 11, 1)), 2026, 11)
    assert not ativo_no_mes(inv(resgate=date(2026, 10, 31)), 2026, 11)

def test_comeca_no_meio_do_mes():
    r = rendimento_no_mes(inv(inicio=date(2026, 3, 15)), 2026, 3)
    esperado = 100000 * (1.12 ** (16 / 365) - 1)     
    assert abs(r.lucro_centavos - esperado) <= 1

def test_resgate_no_meio_do_mes():
    r = rendimento_no_mes(inv(resgate=date(2026, 3, 10)), 2026, 3)
    esperado = 100000 * (1.12 ** (68 / 365) - 1.12 ** (59 / 365))
    assert abs(r.lucro_centavos - esperado) <= 1
    assert abs(r.total_centavos - 100000 * 1.12 ** (68 / 365)) <= 1

def test_fora_do_periodo_devolve_none():
    assert rendimento_no_mes(inv(resgate=date(2026, 3, 10)), 2026, 4) is None

def test_resumo_soma_os_investimentos():
    r = resumo_mes([inv(), inv(valor=50000)], 2026, 3)
    assert len(r.itens) == 2
    assert r.lucro_centavos == sum(x.lucro_centavos for x in r.itens)
