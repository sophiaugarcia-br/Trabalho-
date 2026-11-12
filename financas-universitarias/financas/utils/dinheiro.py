from Decimal import Decimal, ROUND_HALF_UP, InvalidOperation

def centavos(texto):
    limpo = texto.strip().replace("R$", "").replace(" ", "")
    limpo = limpo.replace(".","").replace(",", ".")
    try:
        valor = Decimal(limpo)
    except InvalidOperation:
        raise ValueError(f"Valor inválido: {texto!r}")
    return int((valor*100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

def formatar_brl(centavos):
    reais, resto = divmod(abs(centavos), 100)
    texto = f"{reais:,}".replace(",", ".") + f",{resto:02d}"
    sinal = "-" if centavos < 0 else ""
    return f"{sinal}R$ {texto}"
