from datetime import date, timedelta
from types import SimpleNamespace
from financas.servicos.meta_service import calcular_plano, viabilidade

HOJE = date(2026, 11, 12)

def meta(preco, guardado, dias_ate_prazo):
    return SimpleNamespace(
        preco_centavos=preco,
        guardado_centavos=guardado,
        prazo=HOJE + timedelta(days=dias_ate_prazo),
    )

def test_exemplo_da_especificacao():
    plano = calcular_plano(meta(120000, 0, 180), HOJE)
    assert plano.por_mes == 20000      
    assert plano.por_semana == 4615      
    assert plano.semanas == 26
    assert plano.meses == 6

def test_com_valor_ja_guardado():
    plano = calcular_plano(meta(120000, 20000, 30), HOJE)
    assert plano.faltante == 100000
    assert plano.semanas == 5
    assert plano.meses == 1
    assert plano.por_semana == 20000
    assert plano.por_mes == 100000

def test_prazo_vencido():
    plano = calcular_plano(meta(50000, 0, -11), HOJE)
    assert plano.vencida is True
    assert plano.semanas == 1 and plano.meses == 1
    assert plano.por_mes == 50000

def test_meta_atingida():
    plano = calcular_plano(meta(50000, 60000, 90), HOJE)
    assert plano.atingida is True
    assert plano.faltante == 0
    assert plano.por_mes == 0

def test_viabilidade():
    planos = [calcular_plano(meta(120000, 0, 180), HOJE),
              calcular_plano(meta(60000, 0, 60), HOJE)]
    ok = viabilidade(planos, 80000)
    assert ok.viavel is True and ok.folga == 30000
    nao = viabilidade(planos, 40000)
    assert nao.viavel is False and nao.folga == -10000
