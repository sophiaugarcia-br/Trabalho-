from datetime import date, datetime
from types import SimpleNamespace

from financas.servicos import meta_service

_METAS = [
    SimpleNamespace(id=1, produto="Notebook", preco_centavos=350000,
                    guardado_centavos=50000, prazo=date(2027, 3, 1)),
    SimpleNamespace(id=2, produto="Fone de ouvido", preco_centavos=40000,
                    guardado_centavos=10000, prazo=date(2027, 1, 15)),
]
_proximo_id = 3
SOBRA_MEDIA = 150000 


def _para_centavos(texto):
    
    return round(float(texto.replace(",", ".")) * 100)


def painel_metas(hoje):
    itens = [{"meta": m, "plano": meta_service.calcular_plano(m, hoje)} for m in _METAS]
    viab = meta_service.viabilidade([i["plano"] for i in itens], SOBRA_MEDIA)
    return {"itens": itens, "viabilidade": viab}


def cadastrar_meta(dados):
    global _proximo_id
    erros = []
    produto = dados.get("produto", "").strip()
    if not produto:
        erros.append("Informe o produto.")

    preco = 0
    try:
        preco = _para_centavos(dados.get("preco", ""))
        if preco <= 0:
            erros.append("O preço deve ser maior que zero.")
    except ValueError:
        erros.append("Preço inválido.")

    prazo = None
    try:
        prazo = datetime.strptime(dados.get("prazo", ""), "%Y-%m-%d").date()
        if prazo <= date.today():
            erros.append("O prazo deve ser uma data futura.")
    except ValueError:
        erros.append("Informe um prazo válido (por enquanto é obrigatório).")

    if erros:
        return erros

    _METAS.append(SimpleNamespace(id=_proximo_id, produto=produto,
                                  preco_centavos=preco, guardado_centavos=0, prazo=prazo))
    _proximo_id += 1
    return []


def registrar_aporte(meta_id, valor):
    try:
        centavos = _para_centavos(valor)
    except ValueError:
        return ["Valor inválido."]
    if centavos <= 0:
        return ["O valor deve ser maior que zero."]
    for m in _METAS:
        if m.id == meta_id:
            m.guardado_centavos += centavos
    return []


def concluir(meta_id):
    _METAS[:] = [m for m in _METAS if m.id != meta_id]