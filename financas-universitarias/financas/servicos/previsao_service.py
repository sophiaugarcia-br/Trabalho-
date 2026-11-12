
from dataclasses import dataclass
from datetime import date, timedelta
from financas.servicos.resumo_service import resumo_mes, ENTRADA, SAIDA
from financas.utils.datas import fim_mes, iterar_meses
from financas.utils.dinheiro import dividir_centavos

DIAS_JANELA = 28        
INTERVALO_DIAS = 7     

@dataclass(frozen=True)
class Previsao:
    gerada_em: date
    realizado_centavos: int
    agendado_entradas_centavos: int
    agendado_saidas_centavos: int
    variavel_centavos: int
    saldo_projetado_centavos: int
    situacao: str                 
    historico_suficiente: bool    


def _ocorrencias_mensais(rec, inicio, fim):
    datas = []
    for ano, mes in iterar_meses(inicio, fim):
        dia = min(rec.dia, fim_mes(ano, mes).day)  
        d = date(ano, mes, dia)
        if inicio <= d <= fim:
            datas.append(d)
    return datas

def _ocorrencias_semanais(rec, inicio, fim):
    atraso = (rec.dia - inicio.weekday()) % 7      
    d = inicio + timedelta(days=atraso)
    datas = []
    while d <= fim:
        datas.append(d)
        d += timedelta(days=7)
    return datas

def ocorrencias(rec, inicio, fim):
    inicio = max(inicio, rec.data_inicio)
    if rec.data_fim is not None:
        fim = min(fim, rec.data_fim)
    if inicio > fim:
        return []
    if rec.periodicidade == "MENSAL":
        return _ocorrencias_mensais(rec, inicio, fim)
    if rec.periodicidade == "SEMANAL":
        return _ocorrencias_semanais(rec, inicio, fim)
    raise ValueError(f"Periodicidade inválida: {rec.periodicidade!r}")


def materializar_recorrencias(trans_repo, rec_repo, hoje):
  
    recs = rec_repo.listar()
    if not recs:
        return 0
    primeiro = min(r.data_inicio for r in recs)
    existentes = {
        (t.recorrencia_id, t.data)
        for t in trans_repo.listar((primeiro, hoje))
        if t.recorrencia_id is not None
    }
    criados = 0
    for rec in recs:
        for d in ocorrencias(rec, rec.data_inicio, hoje):
            if (rec.id, d) in existentes:
                continue
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

    amanha = hoje + timedelta(days=1)
    fim = fim_mes(hoje.year, hoje.month)
    futuras = []
    for rec in rec_repo.listar():
        for d in ocorrencias(rec, amanha, fim):
            futuras.append((rec, d))
    return futuras


def gasto_variavel_projetado(trans_repo, hoje):
   
    inicio = hoje - timedelta(days=DIAS_JANELA - 1)
    saidas = [t for t in trans_repo.listar((inicio, hoje), SAIDA)
              if t.recorrencia_id is None]
    total = sum(t.valor_centavos for t in saidas)
    dias_restantes = (fim_mes(hoje.year, hoje.month) - hoje).days
    # (total / 4 semanas) * (dias_restantes / 7)  =  total * dias_restantes / 28
    projetado = dividir_centavos(total * dias_restantes, DIAS_JANELA)
    return projetado, total > 0

def gerar_previsao(trans_repo, rec_repo, hoje):
  
    realizado = resumo_mes(trans_repo, hoje.year, hoje.month, hoje).saldo_centavos

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



def deve_regerar(ultima_data, hoje):
   
    return ultima_data is None or (hoje - ultima_data).days >= INTERVALO_DIAS

def registrar_previsao_semanal(trans_repo, rec_repo, prev_repo, hoje):
   
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
