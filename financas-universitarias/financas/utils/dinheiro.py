"""
Funções para trabalhar com dinheiro em centavos (inteiro).

Todo o sistema guarda valores em centavos (R$ 12,50 = 1250) para evitar os
erros de arredondamento do float. Este módulo converte e
formata dinheiro.
"""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


def para_centavos(texto):
    """Converte texto em reais para centavos (int).

    Aceita "12.50", "1.250,00" e "R$ 3,00".
    Levanta ValueError se o texto não for um número.
    """
    limpo = texto.strip().replace("R$", "").replace(" ", "")
    if "," in limpo:  # formato brasileiro: ponto = milhar, vírgula = decimal
        limpo = limpo.replace(".", "").replace(",", ".")
    try:
        valor = Decimal(limpo)
    except InvalidOperation:  # o Decimal falha se o texto não for número
        raise ValueError(f"Valor inválido: {texto!r}")
    # multiplica por 100 e arredonda a metade para cima (12,505 -> 1251)
    return int((valor * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def formatar_brl(centavos: int) -> str:
    """Formata um valor em centavos para moeda BRL sem separador de milhar."""
    sinal = "-" if centavos < 0 else ""
    absoluto = abs(centavos)
    reais = absoluto // 100
    resto_centavos = absoluto % 100
    return f"{sinal}R$ {reais},{resto_centavos:02d}"


def dividir_centavos(centavos: int, divisor: int) -> int:
    """Divide centavos por um inteiro, arredondando para o centavo mais próximo.

    Usa só inteiros: (2c + d) // (2d) é o mesmo que arredondar c / d com a
    metade subindo, sem passar por float.
    """
    return (2 * centavos + divisor) // (2 * divisor)


def arredondar_centavos(valor):
    """Arredonda um Decimal para centavos inteiros (metade para cima)."""
    return int(valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
