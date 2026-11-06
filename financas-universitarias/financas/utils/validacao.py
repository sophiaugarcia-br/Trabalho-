
from datetime import datetime
from typing import Any, Dict, List

def validar_formulario(dados: Dict[str, Any]) -> List[str]:
    erros = []
    campos_obrigatorios = ["descricao", "valor", "data"]
    for campo in campos_obrigatorios:
        valor_campo = dados.get(campo)
        if valor_campo is None or str(valor_campo).strip() == "":
            erros.append(f"O campo '{campo}' é obrigatório.")
          
    if "valor" in dados and dados["valor"] is not None and str(dados["valor"]).strip() != "":
        try:
            valor_numerico = float(dados["valor"])
            if valor_numerico <= 0:
                erros.append("O campo 'valor' deve ser maior que zero.")
        except (ValueError, TypeError):
            erros.append("O campo 'valor' deve ser um número válido.")
          
    if "data" in dados and dados["data"] is not None and str(dados["data"]).strip() != "":
        data_str = str(dados["data"]).strip()
        data_valida = False
        
        for formato in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                datetime.strptime(data_str, formato)
                data_valida = True
                break
            except ValueError:
                continue
                
        if not data_valida:
            erros.append("O campo 'data' deve ser uma data válida (formatos aceitos: AAAA-MM-DD ou DD/MM/AAAA).")

    return erros
