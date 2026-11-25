
"""
Recorrências (contas e ganhos fixos) e previsão de fim de mês.

Regras principais:
    - As recorrências viram lançamentos reais ("materializar") quando a data chega.
    - A previsão estima se o mês termina em LUCRO ou DÍVIDA:
          saldo = realizado + agendado_entradas - agendado_saidas - variavel
    - Uma nova previsão é gravada a cada 7 dias, ao abrir o programa.

Convenções do projeto: dinheiro em centavos (int) e datas como date.
Os repositórios entram como parâmetros.
"""
from dataclasses import dataclass
from datetime import date, timedelta

# No resumo_service os tipos se chamam TIPO_ENTRADA e TIPO_SAIDA;
# aqui usamos os apelidos ENTRADA e SAIDA.
from financas.servicos.resumo_service import (
    resumo_mes, TIPO_ENTRADA as ENTRADA, TIPO_SAIDA as SAIDA)
from financas.utils.datas import fim_mes, iterar_meses
from financas.utils.dinheiro import dividir_centavos

DIAS_JANELA = 28       # janela de 4 semanas para estimar o gasto variável
INTERVALO_DIAS = 7     # a previsão é regerada a cada 7 dias


@dataclass(frozen=True)
class Previsao:
    """Resultado de uma previsão (imutável). Valores em centavos."""
    gerada_em: date
    realizado_centavos: int           # entradas - saídas do mês, até hoje
    agendado_entradas_centavos: int   # entradas fixas que ainda vão acontecer no mês
    agendado_saidas_centavos: int     # saídas fixas que ainda vão acontecer no mês
    variavel_centavos: int            # estimativa de gastos variáveis até o fim do mês
    saldo_projetado_centavos: int     # saldo estimado no fim do mês
    situacao: str                     # "LUCRO" ou "DIVIDA"
    historico_suficiente: bool        # False = sem gastos variáveis recentes para estimar


# Datas de cada recorrência
# ---------------------------------------------------------------------------
def _ocorrencias_mensais(rec, inicio, fim):
    """Datas em que uma recorrência MENSAL cai entre inicio e fim (inclusive).

    rec.dia é o dia do mês (1 a 31). Em meses mais curtos, usa o último dia
    (dia 31 em fevereiro vira 28 ou 29).
    """
    datas = []
    for ano, mes in iterar_meses(inicio, fim):
        dia = min(rec.dia, fim_mes(ano, mes).day)  # ajusta para meses curtos
        d = date(ano, mes, dia)
        if inicio <= d <= fim:  # descarta datas fora do período pedido
            datas.append(d)
    return datas


def _ocorrencias_semanais(rec, inicio, fim):
    """Datas em que uma recorrência SEMANAL cai entre inicio e fim (inclusive).

    rec.dia é o dia da semana no padrão do Python (0 = segunda ... 6 = domingo).
    """
    # quantos dias faltam, a partir de 'inicio', até o dia da semana da recorrência
    atraso = (rec.dia - inicio.weekday()) % 7
    d = inicio + timedelta(days=atraso)
    datas = []
    while d <= fim:
        datas.append(d)
        d += timedelta(days=7)  # a cada semana
    return datas


def ocorrencias(rec, inicio, fim):
    """Datas de uma recorrência no período, respeitando o início e o fim dela.

    Escolhe a regra pela periodicidade ("MENSAL" ou "SEMANAL").
    Levanta ValueError se a periodicidade for outra.
    """
    inicio = max(inicio, rec.data_inicio)    # não vale antes de a recorrência começar
    if rec.data_fim is not None:
        fim = min(fim, rec.data_fim)         # nem depois de ela terminar
    if inicio > fim:
        return []
    if rec.periodicidade == "MENSAL":
        return _ocorrencias_mensais(rec, inicio, fim)
    if rec.periodicidade == "SEMANAL":
        return _ocorrencias_semanais(rec, inicio, fim)
    raise ValueError(f"Periodicidade inválida: {rec.periodicidade!r}")


# Recorrências -> lançamentos reais
# ---------------------------------------------------------------------------
def materializar_recorrencias(trans_repo, rec_repo, hoje):
    """Cria os lançamentos das recorrências que já venceram (até hoje).

    Não duplica: confere os pares (recorrencia_id, data) que já existem.
    Devolve quantos lançamentos novos foram criados.
    """
    recs = rec_repo.listar()
    if not recs:
        return 0
    primeiro = min(r.data_inicio for r in recs)
    # conjunto de (recorrência, data) já lançados, para não repetir
    existentes = {
        (t.recorrencia_id, t.data)
        for t in trans_repo.listar((primeiro, hoje))
        if t.recorrencia_id is not None
    }
    criados = 0
    for rec in recs:
        for d in ocorrencias(rec, rec.data_inicio, hoje):
            if (rec.id, d) in existentes:
                continue  # já foi lançado antes
            trans_repo.inserir(
                tipo=rec.tipo,
                descricao=rec.descricao,
                valor_centavos=rec.valor_centavos,
                data=d,
                categoria_id=rec.categoria_id,
                recorrencia_id=rec.id,
            )
            criados += 1
    return criados


def ocorrencias_futuras(rec_repo, hoje):
    """Recorrências que ainda vão acontecer, de amanhã até o fim do mês.

    Devolve uma lista de pares (recorrência, data).
    """
    amanha = hoje + timedelta(days=1)
    fim = fim_mes(hoje.year, hoje.month)
    futuras = []
    for rec in rec_repo.listar():
        for d in ocorrencias(rec, amanha, fim):
            futuras.append((rec, d))
    return futuras


# Previsão
# ---------------------------------------------------------------------------
def gasto_variavel_projetado(trans_repo, hoje):
    """Estima os gastos variáveis (não recorrentes) até o fim do mês.

    Usa a média das saídas dos últimos 28 dias e projeta para os dias que
    faltam. Devolve (valor_projetado_em_centavos, historico_suficiente).
    """
    inicio = hoje - timedelta(days=DIAS_JANELA - 1)
    # só saídas que não vieram de recorrência
    saidas = [t for t in trans_repo.listar((inicio, hoje), SAIDA)
              if t.recorrencia_id is None]
    total = sum(t.valor_centavos for t in saidas)
    dias_restantes = (fim_mes(hoje.year, hoje.month) - hoje).days
    # (total / 4 semanas) * (dias_restantes / 7)  =  total * dias_restantes / 28
    projetado = dividir_centavos(total * dias_restantes, DIAS_JANELA)
    return projetado, total > 0


def gerar_previsao(trans_repo, rec_repo, hoje):
    """Calcula a previsão de fim de mês e devolve um objeto Previsao.

    saldo = realizado + agendado_entradas - agendado_saidas - variavel
    """
    # saldo do mês até hoje; resumo_mes devolve um dicionário
    realizado = resumo_mes(trans_repo, hoje.year, hoje.month, hoje)["saldo_centavos"]

    entradas = saidas = 0
    for rec, _ in ocorrencias_futuras(rec_repo, hoje):
        if rec.tipo == ENTRADA:
            entradas += rec.valor_centavos
        elif rec.tipo == SAIDA:
            saidas += rec.valor_centavos

    variavel, suficiente = gasto_variavel_projetado(trans_repo, hoje)
    saldo = realizado + entradas - saidas - variavel
    return Previsao(
        gerada_em=hoje,
        realizado_centavos=realizado,
        agendado_entradas_centavos=entradas,
        agendado_saidas_centavos=saidas,
        variavel_centavos=variavel,
        saldo_projetado_centavos=saldo,
        situacao="DIVIDA" if saldo < 0 else "LUCRO",
        historico_suficiente=suficiente,
    )


# Regra dos 7 dias
# ---------------------------------------------------------------------------
def deve_regerar(ultima_data, hoje):
    """True se nunca houve previsão ou se já passaram 7 dias desde a última."""
    return ultima_data is None or (hoje - ultima_data).days >= INTERVALO_DIAS


def registrar_previsao_semanal(trans_repo, rec_repo, prev_repo, hoje):
    """Gera e grava uma nova previsão se já passaram 7 dias.

    Devolve a Previsao gerada, ou None se ainda não era hora.
    """
    ultima = prev_repo.ultima()
    if not deve_regerar(ultima.gerada_em if ultima else None, hoje):
        return None
    previsao = gerar_previsao(trans_repo, rec_repo, hoje)
    prev_repo.inserir(
        gerada_em=previsao.gerada_em,
        saldo_projetado_centavos=previsao.saldo_projetado_centavos,
        situacao=previsao.situacao,
    )
    return previsao
