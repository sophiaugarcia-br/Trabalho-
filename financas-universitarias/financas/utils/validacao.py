"""Validações de formulários e dados de lançamentos."""
from datetime import date, datetime

from financas.utils.dinheiro import para_centavos

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


def normalizar_data(texto):
    if isinstance(texto, datetime):
        return texto.date().isoformat()
    if isinstance(texto, date):
        return texto.isoformat()
    return datetime.strptime(str(texto).strip(), "%Y-%m-%d").date().isoformat()


def validar_data(texto, campo="Data"):
    erros = validar_obrigatorio(texto, campo)
    if erros:
        return erros
    try:
        normalizar_data(texto)
    except (ValueError, TypeError):
        return [f"{campo} inválida (use AAAA-MM-DD)."]
    return []


def validar_categoria_id(valor):
    try:
        categoria_id = int(valor)
        if categoria_id <= 0 or str(valor).strip() != str(categoria_id):
            raise ValueError
    except (ValueError, TypeError):
        return ["Categoria inválida."]
    return []


def validar_lancamento(dados):
    erros = []
    if dados.get("tipo") not in TIPOS_VALIDOS:
        erros.append("Tipo deve ser ENTRADA ou SAIDA.")

    erros += validar_obrigatorio(dados.get("descricao"), "Descrição")
    erros += validar_valor(dados.get("valor"))
    erros += validar_data(dados.get("data"))
    erros += validar_categoria_id(dados.get("categoria_id"))
    return erros


    return erros  
