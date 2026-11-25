

from datetime import date
import pytest
from financas.servicos.resumo_service import (
    resumo_mes,
    listar_extrato,
    registrar_lancamento,
    _semana_do_mes,
    dados_graficos,
)

HOJE = date(2026, 11, 12)


class RepoFalso:
    def __init__(self, transacoes=(), categorias=None):
        self.transacoes = list(transacoes)
        self.categorias = categorias or {}
        self.inseridos = []

    def listar(self, periodo, tipo=None, categoria_id=None):
        inicio, fim = periodo
        resultado = []
        for t in self.transacoes:
            data_t = date.fromisoformat(t["data"]) if isinstance(t["data"], str) else t["data"]
            if (
                inicio <= data_t <= fim
                and (tipo is None or t["tipo"] == tipo)
                and (categoria_id is None or t.get("categoria_id") == categoria_id)
            ):
                resultado.append(t)
        return resultado

    def inserir(self, campos):
        self.inseridos.append(campos)
        return len(self.inseridos)

    def somar_por_categoria(self, periodo, tipo):
        inicio, fim = periodo
        totais = {}
        for t in self.transacoes:
            data_t = date.fromisoformat(t["data"]) if isinstance(t["data"], str) else t["data"]
            if inicio <= data_t <= fim and t["tipo"] == tipo:
                cat_id = t.get("categoria_id")
                totais[cat_id] = totais.get(cat_id, 0) + t["valor_centavos"]

        linhas = []
        for cat_id, total in totais.items():
            cat = self.categorias.get(cat_id, {})
            linhas.append({
                "categoria_id": cat_id,
                "nome": cat.get("nome", f"Categoria {cat_id}"),
                "cor": cat.get("cor", "#000000"),
                "total_centavos": total,
            })
        return linhas


def t(tipo, valor, dia, cat=1, mes=11):
    return {
        "id": 0,
        "tipo": tipo,
        "descricao": "x",
        "valor_centavos": valor,
        "data": date(2026, mes, dia),
        "categoria_id": cat,
    }


CATEGORIAS = {
    1: {"nome": "Alimentação", "cor": "#D1495B"},
    2: {"nome": "Transporte", "cor": "#1F6F8B"},
}


@pytest.fixture
def repo():
    return RepoFalso(
        transacoes=[
            t("ENTRADA", 100000, 5),
            t("SAIDA", 30000, 10, cat=1),
            t("SAIDA", 5000, 20, cat=2),
            t("SAIDA", 999, 31, mes=10),
        ],
        categorias=CATEGORIAS,
    )


def test_resumo_vai_so_ate_hoje(repo):
    r = resumo_mes(repo, 2026, 11, HOJE)
    assert r["entradas_centavos"] == 100000
    assert r["saidas_centavos"] == 30000
    assert r["saldo_centavos"] == 70000
    assert r["quantidade"] == 2


def test_resumo_de_mes_fechado(repo):
    r = resumo_mes(repo, 2026, 10, HOJE)
    assert r["saidas_centavos"] == 999


def test_resumo_de_mes_futuro(repo):
    r = resumo_mes(repo, 2026, 12, HOJE)
    assert (r["entradas_centavos"], r["saidas_centavos"], r["saldo_centavos"]) == (0, 0, 0)


def test_extrato_ordenado_e_filtrado(repo):
    todos = listar_extrato(repo, {"ano": 2026, "mes": 11})
    assert [x["data"].day for x in todos] == [20, 10, 5]

    saidas = listar_extrato(repo, {"ano": 2026, "mes": 11, "tipo": "SAIDA"})
    assert [x["data"].day for x in saidas] == [20, 10]


def test_registrar_valido():
    repo = RepoFalso()
    dados = {
        "tipo": "SAIDA",
        "descricao": " Almoço ",
        "valor": "25,90",
        "data": "2026-11-12",
        "categoria_id": "1",
    }
    resultado = registrar_lancamento(repo, dados)
    assert resultado == {"ok": True, "id": 1, "erros": []}

    campos = repo.inseridos[0]
    assert campos["valor_centavos"] == 2590
    assert campos["descricao"] == "Almoço"
    assert campos["data"] == "2026-11-12"
    assert campos["categoria_id"] == "1"


def test_registrar_invalido_nao_salva():
    repo = RepoFalso()
    dados = {
        "tipo": "SAIDA",
        "descricao": "",
        "valor": "0",
        "data": "2026-11-12",
        "categoria_id": "1",
    }
    resultado = registrar_lancamento(repo, dados)
    assert resultado["ok"] is False
    assert len(resultado["erros"]) == 2
    assert repo.inseridos == []


def test_semana_do_mes():
    assert _semana_do_mes(7) == 1
    assert _semana_do_mes(8) == 2
    assert _semana_do_mes(29) == 5


def test_graficos_colunas_e_pizza(repo):
    g = dados_graficos(repo, 2026, 11)
    assert len(g["colunas"]["rotulos"]) == 5
    assert g["colunas"]["saidas"] == [0.0, 300.0, 50.0, 0.0, 0.0]
    assert g["pizza"]["ids"] == [1, 2]
    assert g["pizza"]["rotulos"] == ["Alimentação", "Transporte"]
    assert g["pizza"]["valores"] == [300.0, 50.0]


def test_graficos_filtro_por_categoria(repo):
    g = dados_graficos(repo, 2026, 11, categoria_id=2)
    assert g["colunas"]["saidas"] == [0.0, 0.0, 50.0, 0.0, 0.0]


def test_graficos_filtro_entradas(repo):
    g = dados_graficos(repo, 2026, 11, filtro="entradas")
    assert g["colunas"]["entradas"] == [1000.0, 0.0, 0.0, 0.0, 0.0]
    assert g["pizza"]["valores"] == [1000.0]
