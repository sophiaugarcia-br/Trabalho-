
"""Conversões e operações monetárias usando centavos inteiros."""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


def para_centavos(texto):
    """Converte reais em texto para centavos; aceita formato BR ou internacional."""
    if texto is None:
        raise ValueError("Valor não informado.")

    limpo = str(texto).strip().replace("R$", "").replace(" ", "")
    if not limpo:
        raise ValueError("Valor não informado.")
    if "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")

    try:
        valor = Decimal(limpo)
    except (InvalidOperation, ValueError):
        raise ValueError(f"Valor inválido: {texto!r}")

    if not valor.is_finite():
        raise ValueError("O valor precisa ser finito.")

    return int((valor * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def formatar_brl(centavos: int) -> str:
    sinal = "-" if centavos < 0 else ""
    absoluto = abs(int(centavos))
    return f"{sinal}R$ {absoluto // 100},{absoluto % 100:02d}"


def dividir_centavos(centavos: int, divisor: int) -> int:
    if divisor <= 0:
        raise ValueError("O divisor deve ser maior que zero.")
    sinal = -1 if centavos < 0 else 1
    absoluto = abs(int(centavos))
    return sinal * ((2 * absoluto + divisor) // (2 * divisor))


def arredondar_centavos(valor):
    return int(Decimal(valor).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
