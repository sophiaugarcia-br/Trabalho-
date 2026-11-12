
import calendar
from datetime import date 

def inicio_mees(ano, mes):
  return date(ano, mes,1)

def fim_mes(ano, mes):
  ultimo_dia = calendar.monthrange(ano, mes)[1]
  return date(ano, mes, ultimo_dia)
  
def somar_meses(data, n):
  indice = data.year * 12 + (data.month - 1) + n
  ano, mes_zero = divmod(indice, 12)
  mes = mes_zero + 1 
  dia = min(data.day, calendar.monthrange(ano, mes)[1])
  return date(ano, mes, dia)

def iterar_meses(inicio, fim):
  atual = inicio.replace(day=1)
  while atual <= fim:
    yield atual.year, atual.month
    atual = somar_meses(atual, 1)
  
