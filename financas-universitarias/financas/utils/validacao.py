from datetime import date, datetime  
from financas.utils.dinheiro import para_centavos  

TIPOS_VALIDOS = ("ENTRADA", "SAIDA") 


def validar_obrigatorio(texto, campo):
    ''' Verifica se o valor é None ou se, convertido para string e sem espaços nas pontas, fica vazio'''
    if texto is None or not str(texto).strip():
        return [f"{campo} é obrigatório."]  
    return []  


def validar_valor(texto, campo="Valor"):
    ''' Primeiro valida se o valor foi informado'''
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
    """Normaliza date/datetime ou texto no formato ISO AAAA-MM-DD."""
    if isinstance(texto, datetime):
        return texto.date().isoformat()
    if isinstance(texto, date):
        return texto.isoformat()
    data = datetime.strptime(str(texto).strip(), "%Y-%m-%d")
    return data.strftime("%Y-%m-%d")


def validar_data(texto, campo="Data"):
    ''' Verifica se a data foi informada'''
    erros = validar_obrigatorio(texto, campo)
    if erros:
        return erros
    try:
        normalizar_data(texto)
    except ValueError:
        return [f"{campo} inválida (use AAAA-MM-DD)."] 
    return [] 


def validar_lancamento(dados):
    erros = [] 

    # Valida se o campo "tipo" existe e está entre os tipos permitidos
    if dados.get("tipo") not in TIPOS_VALIDOS:
        erros.append("Tipo deve ser ENTRADA ou SAIDA.")

    # Valida os campos obrigatórios e específicos de um lançamento financeiro
    erros += validar_obrigatorio(dados.get("descricao"), "Descrição")
    erros += validar_valor(dados.get("valor"))
    erros += validar_data(dados.get("data"))
    erros += validar_obrigatorio(dados.get("categoria_id"), "Categoria")

    return erros

def validar_categoria_id(categoria_id, campo="Categoria"):
    """Valida se o identificador da categoria é um inteiro positivo."""
    erros = validar_obrigatorio(categoria_id, campo)
    if erros:
        return erros
    try:
        identificador = int(categoria_id)
    except (TypeError, ValueError):
        return [f"{campo} inválida."]
    if identificador <= 0:
        return [f"{campo} inválida."]
    return []

