
from datetime import date, timedelta
from types import SimpleNamespace
import pytest
from financas.servicos.previsao_service import (
    ocorrencias, materializar_recorrencias, gerar_previsao,
    deve_regerar, registrar_previsao_semanal,
)

HOJE = date(2026, 11, 12)


class RepoTransacoesFalso:
    def __init__(self, transacoes=()):
        self.transacoes = list(transacoes)

    def listar(self, periodo, tipo=None, categoria_id=None):
        inicio, fim = periodo
        return [t for t in self.transacoes
                if inicio <= t.data <= fim
                and (tipo is None or t.tipo == tipo)
                and (categoria_id is None or t.categoria_id == categoria_id)]

    def inserir(self, **campos):
        novo = SimpleNamespace(id=len(self.transacoes) + 1, **campos)
        self.transacoes.append(novo)
        return novo.id

class RepoRecorrenciasFalso:
    def __init__(self, recs=()):
        self.recs = list(recs)

    def listar(self):
        return list(self.recs)

class RepoPrevisaoFalso:
    def __init__(self, ultima_data=None):
        self.registros = []
        if ultima_data:
            self.registros.append(SimpleNamespace(gerada_em=ultima_data))

    def ultima(self):
        return self.registros[-1] if self.registros else None

    def inserir(self, **campos):
        self.registros.append(SimpleNamespace(**campos))

def t(tipo, valor, data, rec=None):
    return SimpleNamespace(id=0, tipo=tipo, descricao="x", valor_centavos=valor,
                           data=data, categoria_id=1, recorrencia_id=rec)

def recorr(id, tipo, valor, periodicidade, dia, inicio, fim=None):
    return SimpleNamespace(id=id, tipo=tipo, descricao=f"rec{id}",
                           valor_centavos=valor, periodicidade=periodicidade,
                           dia=dia, data_inicio=inicio, data_fim=fim,
                           categoria_id=1)


def test_mensal_dia_31_se_ajusta_ao_mes():
    r = recorr(1, "SAIDA", 100, "MENSAL", 31, date(2026, 1, 1))
    assert ocorrencias(r, date(2026, 1, 1), date(2026, 4, 30)) == [
        date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31), date(2026, 4, 30)]

def test_mensal_respeita_data_inicio():
    r = recorr(1, "SAIDA", 100, "MENSAL", 5, date(2026, 3, 10))
    assert ocorrencias(r, date(2026, 3, 1), date(2026, 5, 31)) == [
        date(2026, 4, 5), date(2026, 5, 5)]

def test_mensal_respeita_data_fim():
    r = recorr(1, "SAIDA", 100, "MENSAL", 5, date(2026, 1, 1), date(2026, 3, 5))
    assert ocorrencias(r, date(2026, 1, 1), date(2026, 12, 31)) == [
        date(2026, 1, 5), date(2026, 2, 5), date(2026, 3, 5)]

def test_semanal_toda_segunda():
    r = recorr(1, "SAIDA", 100, "SEMANAL", 0, date(2026, 11, 1))
    datas = ocorrencias(r, date(2026, 11, 1), date(2026, 11, 30))
    assert [d.day for d in datas] == [2, 9, 16, 23, 30]

def test_periodicidade_invalida():
    r = recorr(1, "SAIDA", 100, "ANUAL", 1, date(2026, 1, 1))
    with pytest.raises(ValueError):
        ocorrencias(r, date(2026, 1, 1), date(2026, 12, 31))



def test_materializar_cria_e_nao_duplica():
    trans = RepoTransacoesFalso()
    recs = RepoRecorrenciasFalso(
        [recorr(1, "SAIDA", 150000, "MENSAL", 5, date(2026, 9, 1))])
    assert materializar_recorrencias(trans, recs, HOJE) == 3
    assert sorted(x.data for x in trans.transacoes) == [
        date(2026, 9, 5), date(2026, 10, 5), date(2026, 11, 5)]
    assert all(x.recorrencia_id == 1 for x in trans.transacoes)
    assert materializar_recorrencias(trans, recs, HOJE) == 0   # rodar de novo não duplica
    assert len(trans.transacoes) == 3

def test_materializar_sem_recorrencias():
    assert materializar_recorrencias(
        RepoTransacoesFalso(), RepoRecorrenciasFalso(), HOJE) == 0



@pytest.fixture
def trans():
    return RepoTransacoesFalso([
        t("ENTRADA", 100000, date(2026, 11, 5)),
        t("SAIDA", 30000, date(2026, 11, 10)),
        t("SAIDA", 56000, date(2026, 10, 20)),            
        t("SAIDA", 20000, date(2026, 10, 1)),             
        t("SAIDA", 50000, date(2026, 11, 5), rec=1),    
    ])

@pytest.fixture
def recs():
    return RepoRecorrenciasFalso([
        recorr(1, "SAIDA", 50000, "MENSAL", 5, date(2026, 9, 1)),    
        recorr(2, "ENTRADA", 40000, "MENSAL", 20, date(2026, 9, 1)), 
        recorr(3, "SAIDA", 2000, "SEMANAL", 0, date(2026, 10, 1)),   
        recorr(4, "SAIDA", 9900, "MENSAL", 25, date(2026, 1, 1),
               date(2026, 10, 31)),                                  
    ])

def test_previsao_completa(trans, recs):
    p = gerar_previsao(trans, recs, HOJE)
    assert p.realizado_centavos == 20000        
    assert p.agendado_entradas_centavos == 40000
    assert p.agendado_saidas_centavos == 6000    
    assert p.variavel_centavos == 55286          
    assert p.saldo_projetado_centavos == -1286    
    assert p.situacao == "DIVIDA"
    assert p.historico_suficiente is True

def test_previsao_sem_historico():
    trans = RepoTransacoesFalso([t("ENTRADA", 100000, date(2026, 11, 5))])
    p = gerar_previsao(trans, RepoRecorrenciasFalso(), HOJE)
    assert p.variavel_centavos == 0
    assert p.historico_suficiente is False
    assert p.saldo_projetado_centavos == 100000
    assert p.situacao == "LUCRO"

def test_previsao_no_ultimo_dia_do_mes(trans, recs):
    p = gerar_previsao(trans, recs, date(2026, 11, 30))
    assert p.agendado_entradas_centavos == 0
    assert p.agendado_saidas_centavos == 0
    assert p.variavel_centavos == 0
    assert p.saldo_projetado_centavos == p.realizado_centavos


def test_deve_regerar():
    assert deve_regerar(None, HOJE) is True
    assert deve_regerar(HOJE - timedelta(days=6), HOJE) is False
    assert deve_regerar(HOJE - timedelta(days=7), HOJE) is True

def test_registrar_so_quando_e_hora(trans, recs):
    prev = RepoPrevisaoFalso()
    primeira = registrar_previsao_semanal(trans, recs, prev, HOJE)
    assert primeira is not None and len(prev.registros) == 1
    assert prev.registros[0].situacao == "DIVIDA"
   
    assert registrar_previsao_semanal(trans, recs, prev, HOJE) is None
    assert len(prev.registros) == 1
  
    assert registrar_previsao_semanal(trans, recs, prev, HOJE + timedelta(days=7)) is not None
    assert len(prev.registros) == 2
