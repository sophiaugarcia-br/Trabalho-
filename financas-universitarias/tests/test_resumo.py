from datetime import date
import pytest

from financas.servicos.resumo_service import (
    _semana_do_mes,
    dados_graficos,
    listar_extrato,
    registrar_lancamento,
    resumo_mes,
)

HOJE = date(2026, 11, 12)

CATEGORIAS = {
    1: {"nome": "Alimentação", "cor": "#D1495B"},
    2: {"nome": "Transporte", "cor": "#1F6F8B"},
}


class TransacaoItem(dict):
    """Permite acessar campos tanto como dict (t['data']) quanto como atributo (t.data)."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class RepoFalso:
    def __init__(self, transacoes=(), categorias=None):
        self.transacoes = [TransacaoItem(tr) for tr in transacoes]
        self.categorias = categorias or CATEGORIAS
        self.inseridos = []

    def listar(self, periodo, tipo=None, categoria_id=None):
        inicio, fim = periodo
        resultado = []
        for tr in self.transacoes:
            tr_data = date.fromisoformat(tr["data"]) if isinstance(tr["data"], str) else tr["data"]
            if (
                inicio <= tr_data <= fim
                and (tipo is None or tr["tipo"] == tipo)
                and (categoria_id is None or tr.get("categoria_id") == categoria_id)
            ):
                resultado.append(tr)
        return resultado

    def inserir(self, campos):
        self.inseridos.append(campos)
        return len(self.inseridos)

    def somar_por_categoria(self, periodo, tipo):
        totais = {}
        for tr in self.listar(periodo, tipo=tipo):
            cat_id = tr.get("categoria_id")
            if cat_id in self.categorias:
                totais[cat_id] = totais.get(cat_id, 0) + tr["valor_centavos"]

        linhas = []
        for cat_id, total in totais.items():
            cat = self.categorias[cat_id]
            linhas.append({
                "categoria_id": cat_id,
                "nome": cat["nome"],
                "cor": cat["cor"],
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


def test_resumo_de_mes_fechado(repo):
    r = resumo_mes(repo, 2026, 10, HOJE)
    assert r["saidas_centavos"] == 999


def test_resumo_de_mes_futuro(repo):
    r = resumo_mes(repo, 2026, 12, HOJE)
    assert (r["entradas_centavos"], r["saidas_centavos"], r["saldo_centavos"]) == (0, 0, 0)


def test_extrato_ordenado_e_filtrado(repo):
    extrato = listar_extrato(repo, {"ano": 2026, "mes": 11})
    assert [x["data"].day for x in extrato] == [20, 10, 5]

    saidas = listar_extrato(repo, {"ano": 2026, "mes": 11, "tipo": "SAIDA"})
    assert [x["data"].day for x in saidas] == [20, 10]


def test_registrar_valido(monkeypatch):
    from financas.servicos import resumo_service

    monkeypatch.setattr(resumo_service.validacao, "validar_lancamento", lambda _d: [])
    monkeypatch.setattr(resumo_service.validacao, "normalizar_data", lambda d: date.fromisoformat(d))

    repo_local = RepoFalso()
    dados = {
        "tipo": "SAIDA",
        "descricao": " Almoço ",
        "valor": "25,90",
        "data": "2026-11-12",
        "categoria_id": 1,
    }
    res = registrar_lancamento(repo_local, dados)
    assert res["ok"] is True
    assert res["id"] == 1
    assert res["erros"] == []

    campos = repo_local.inseridos[0]
    assert campos["valor_centavos"] == 2590
    assert campos["descricao"] == "Almoço"
    assert campos["data"] == "2026-11-12"
    assert campos["categoria_id"] == "1"



def test_registrar_invalido_nao_salva(monkeypatch):
    from financas.servicos import resumo_service

    monkeypatch.setattr(
        resumo_service.validacao,
        "validar_lancamento",
        lambda _d: ["Descrição obrigatória", "Valor inválido"],
    )

    repo_local = RepoFalso()
    dados = {
        "tipo": "SAIDA",
        "descricao": "",
        "valor": "0",
        "data": "2026-11-12",
        "categoria_id": 1,
    }
    res = registrar_lancamento(repo_local, dados)
    assert res["ok"] is False
    assert res.get("id") is None
    assert len(res["erros"]) == 2
    assert repo_local.inseridos == []



def test_semana_do_mes():
    # _semana_do_mes retorna índice de 0 a 4 a partir do dia (int)
    assert _semana_do_mes(7) == 0
    assert _semana_do_mes(8) == 1
    assert _semana_do_mes(29) == 4


def test_graficos_colunas_e_pizza(repo):
    g = dados_graficos(repo, 2026, 11, filtro="saidas")
    assert len(g["colunas"]["rotulos"]) == 5
    assert g["colunas"]["saidas"] == [0.0, 300.0, 50.0, 0.0, 0.0]
    assert g["pizza"]["ids"] == [1, 2]
    assert g["pizza"]["rotulos"] == ["Alimentação", "Transporte"]
    assert g["pizza"]["valores"] == [300.0, 50.0]


def test_graficos_filtro_por_categoria(repo):
    g = dados_graficos(repo, 2026, 11, filtro="saidas", categoria_id=2)
    assert g["colunas"]["saidas"] == [0.0, 0.0, 50.0, 0.0, 0.0]


def test_graficos_filtro_entradas(repo):
    g = dados_graficos(repo, 2026, 11, filtro="entradas")
    assert g["colunas"]["entradas"] == [1000.0, 0.0, 0.0, 0.0, 0.0]
    assert g["pizza"]["valores"] == [1000.0]
