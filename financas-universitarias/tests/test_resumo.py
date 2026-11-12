
from datetime import date
from types import SimpleNamespace
import pytest
from financas.servicos.resumo_service import (
    resumo_mes, listar_extrato, registrar_lancamento,
    semana_do_mes, dados_graficos,
)

HOJE = date(2026, 11, 12)

class RepoFalso:
    """Imita o repositório real, guardando tudo em memória."""
    def __init__(self, transacoes=()):
        self.transacoes = list(transacoes)
        self.inseridos = []

    def listar(self, periodo, tipo=None, categoria_id=None):
        inicio, fim = periodo
        return [t for t in self.transacoes
                if inicio <= t.data <= fim
                and (tipo is None or t.tipo == tipo)
                and (categoria_id is None or t.categoria_id == categoria_id)]

    def inserir(self, **campos):
        self.inseridos.append(campos)
        return len(self.inseridos)

def t(tipo, valor, dia, cat=1, mes=11):
    return SimpleNamespace(id=0, tipo=tipo, descricao="x", valor_centavos=valor,
                           data=date(2026, mes, dia), categoria_id=cat)

CATEGORIAS = {
    1: SimpleNamespace(nome="Alimentação", cor="#D1495B"),
    2: SimpleNamespace(nome="Transporte", cor="#1F6F8B"),
}

@pytest.fixture
def repo():
    return RepoFalso([
        t("ENTRADA", 100000, 5),
        t("SAIDA", 30000, 10, cat=1),
        t("SAIDA", 5000, 20, cat=2),
        t("SAIDA", 999, 31, mes=10),
    ])

def test_resumo_vai_so_ate_hoje(repo):
    r = resumo_mes(repo, 2026, 11, HOJE)       # o lançamento do dia 20 ainda não conta
    assert r.entradas_centavos == 100000
    assert r.saidas_centavos == 30000
    assert r.saldo_centavos == 70000

def test_resumo_de_mes_fechado(repo):
    assert resumo_mes(repo, 2026, 10, HOJE).saidas_centavos == 999

def test_resumo_de_mes_futuro(repo):
    r = resumo_mes(repo, 2026, 12, HOJE)
    assert (r.entradas_centavos, r.saidas_centavos, r.saldo_centavos) == (0, 0, 0)

def test_extrato_ordenado_e_filtrado(repo):
    assert [x.data.day for x in listar_extrato(repo, 2026, 11)] == [20, 10, 5]
    saidas = listar_extrato(repo, 2026, 11, tipo="SAIDA")
    assert [x.data.day for x in saidas] == [20, 10]

def test_registrar_valido():
    repo = RepoFalso()
    dados = {"tipo": "SAIDA", "descricao": " Almoço ", "valor": "25,90",
             "data": "2026-11-12", "categoria_id": "1"}
    novo_id, erros = registrar_lancamento(repo, dados)
    assert novo_id == 1 and erros == []
    campos = repo.inseridos[0]
    assert campos["valor_centavos"] == 2590
    assert campos["descricao"] == "Almoço"
    assert campos["data"] == date(2026, 11, 12)
    assert campos["categoria_id"] == 1

def test_registrar_invalido_nao_salva():
    repo = RepoFalso()
    dados = {"tipo": "SAIDA", "descricao": "", "valor": "0",
             "data": "2026-11-12", "categoria_id": "1"}
    novo_id, erros = registrar_lancamento(repo, dados)
    assert novo_id is None and len(erros) == 2
    assert repo.inseridos == []

def test_semana_do_mes():
    assert semana_do_mes(date(2026, 11, 7)) == 1
    assert semana_do_mes(date(2026, 11, 8)) == 2
    assert semana_do_mes(date(2026, 11, 29)) == 5

def test_graficos_colunas_e_pizza(repo):
    g = dados_graficos(repo, CATEGORIAS, 2026, 11)
    assert len(g["colunas"]["rotulos"]) == 5
    assert g["colunas"]["series"]["entradas"] == [100000, 0, 0, 0, 0]
    assert g["colunas"]["series"]["saidas"] == [0, 30000, 5000, 0, 0]
    assert g["pizza"]["ids"] == [1, 2]
    assert g["pizza"]["rotulos"] == ["Alimentação", "Transporte"]
    assert g["pizza"]["textos"] == ["R$ 300,00", "R$ 50,00"]

def test_graficos_filtro_por_categoria(repo):
    g = dados_graficos(repo, CATEGORIAS, 2026, 11, categoria_id=2)
    assert g["colunas"]["series"]["saidas"] == [0, 0, 5000, 0, 0]

def test_graficos_filtro_entradas(repo):
    g = dados_graficos(repo, CATEGORIAS, 2026, 11, filtro="entradas")
    assert list(g["colunas"]["series"]) == ["entradas"]
    assert g["pizza"]["valores"] == [100000]

def test_graficos_filtro_invalido(repo):
    with pytest.raises(ValueError):
        dados_graficos(repo, CATEGORIAS, 2026, 11, filtro="banana")
