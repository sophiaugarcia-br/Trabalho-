
from datetime import datetime
from financas.utils.dinheiro import centavos
TIPOS_VALIDOS = ("ENTRADA", "SAIDA")

def validar_obrigatorio(texto, campo):
    if texto is None or not str(texto).strip():
        return [f"{campo} é obrigatório."]
    return []

def validar_valor(texto, campo="Valor"):
    erros = validar_obrigatorio(texto, campo)
    if erros:
        return erros
    try:
        centavos = para_centavos(str(texto))
    except ValueError:
        return [f"{campo} inválido."]
    if centavos <= 0:
        return [f"{campo} deve ser maior que zero."]
    return []

def validar_data(texto, campo="Data"):
    erros = validar_obrigatorio(texto, campo)
    if erros:
        return erros
    try:
        datetime.strptime(str(texto), "%Y"-%m-%d")
    except ValueError:
        return [f"{campo} inválida (use AAAA-MM-DD)."]
    return []

def validar_lancamento(dados):
    """Valida um lançamento inteiro (dicionário do formulário)."""
    erros = []
    if dados.get("tipo") not in TIPOS_VALIDOS:
        erros.append("Tipo deve ser ENTRADA ou SAIDA.")
    erros += validar_obrigatorio(dados.get("descricao"), "Descrição")
    erros += validar_valor(dados.get("valor"))
    erros += validar_data(dados.get("data"))
    erros += validar_obrigatorio(dados.get("categoria_id"), "Categoria")
    return erros
