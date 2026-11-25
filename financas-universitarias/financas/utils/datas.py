"""
Aritmética de calendário usada pelo sistema: limites do mês, soma de meses
e a lista de meses de um período (usada nos relatórios e nas recorrências).
"""
import calendar
from datetime import date

def inicio_mes(ano, mes):
  """Devolve o primeiro dia do mês como date."""
  return date(ano, mes, 1)


def fim_mes(ano, mes):
  """Devolve o último dia do mês como date (considera ano bissexto)."""
  # monthrange devolve (dia da semana do dia 1, quantidade de dias do mês)
  ultimo_dia = calendar.monthrange(ano, mes)[1]
  return date(ano, mes, ultimo_dia)


def somar_meses(data, n):
  """Soma n meses a uma data (n pode ser negativo).

  Se o dia não existir no mês de destino, usa o último dia do mês
  (por exemplo, 31/01 + 1 mês = 28/02).
  """
  # transforma o mês em um número corrido: ano * 12 + (mês - 1)
  indice = data.year * 12 + (data.month - 1) + n
  ano, mes_zero = divmod(indice, 12)  # separa de volta em ano e mês (0 a 11)
  mes = mes_zero + 1
  dia = min(data.day, calendar.monthrange(ano, mes)[1])  # evita datas inexistentes
  return date(ano, mes, dia)


def iterar_meses(inicio, fim):
  """Gera tuplas (ano, mes) de cada mês entre inicio e fim, inclusive.

  Exemplo: for ano, mes in iterar_meses(date(2026, 10, 15), date(2026, 11, 24))
  passa por (2026, 10) e (2026, 11).
  """
  atual = inicio.replace(day=1)  # anda sempre de dia 1 em dia 1
  while atual <= fim:
    yield atual.year, atual.month  # yield entrega um mês de cada vez
    atual = somar_meses(atual, 1)
