
import calendar
from datetime import date, timedelta
from typing import Generator, Tuple

def inicio_mes(d:date) -> date:
  return date(d.year, d.month, 1)

def fim_mes(d: date) -> date:
    ultimo_dia = calendar.monthrange(d.year, d.month)[1]
    return date(d.year, d.month, ultimo_dia)
  
def somar_meses(d:date, meses:int) -> date:
    mes_total = d.month -1 + meses
    ano = d.year + mes_total // 12
    mes = mes_total % 12 + 1
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    dia = min(d.day, ultimo_dia)
    return date(ano, mes, dia)

def iterar_meses(inicio: date, fim: date) -> Generator[date, None, None]:
    atual = inicio_mes(inicio)
    fim_limite = inicio_mes(fim)
    while atual <= fim_limite:
        yield atual
        atual = somar_meses(atual, 1)
