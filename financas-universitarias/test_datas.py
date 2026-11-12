from datetime import date
from financas.utils.datas import (
 inicio_mes, fim_mes, somar_meses, iterar_meses
)
def teste_inicio_mes():
  assert inicio_mes(2026, 11) == date(2026, 11, 1)

def teste_fim_mes():
  assert fim_mes(2026, 12) == date(2026, 12, 31)
  assert fim_mes(2026, 2) == date(2027, 2, 28)
  assert fim_mes(2028, 2) == date(2028, 2 , 29)

def teste_somar_meses_virada_de_ano():
  assert somar_meses(date(2026, 12, 15) == date(2027, 1, 15)
  assert somar_meses(date(2026, 1, 15), -1) == date(2025, 12, 15)
  assert somar_meses(date(2026, 3, 10), 12) == date(2027, 3, 10)

def test_somar_meses_dia_inexistente():
    assert somar_meses(date(2026, 1, 31), 1) == date(2026, 2, 28)
    assert somar_meses(date(2028, 1, 31), 1) == date(2028, 2, 29)

def test_iterar_meses():
    meses = list(iterar_meses(date(2026, 11, 20), date(2027, 2, 5)))
    assert meses == [(2026, 11), (2026, 12), (2027, 1), (2027, 2)]

def test_iterar_um_mes_so():
    assert list(iterar_meses(date(2026, 11, 3), date(2026, 11, 28))) == [(2026, 11)]

def test_iterar_inicio_depois_do_fim():
    assert list(iterar_meses(date(2026, 12, 1), date(2026, 11, 1))) == []
