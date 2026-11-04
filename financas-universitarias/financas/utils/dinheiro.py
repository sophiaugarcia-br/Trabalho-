from Decimal import Decimal, InvalidOperation, ROUND_HALF_UP

def arredondar_centavos(valor: Decimal) -> int:
    return int(valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

def para_centavos(texto) -> int:
  limpo = str(texto).strip().replace("R$","").replace(" ", "")
  if "," in limpo:
    limpo = limpo.replace(".","").replace(",",".")
  try:
    valor= decimal(limpo)
  except InvalidOperation:
    raise ValueError (f'Valor inválido: {texto!r}')
  return arredondar_centavos(valor * 100)


def formatar_brl(centavos: int) -> str:
   sinal = "-" if centavos < 0 else ""
   reais, cent = divmod(abs(centavos), 100)
   reais_fmt = f"{reais:,}".replace(",", ".")
   return f"{sinal}R$ {reais_fmt},{cent:02d}"


