import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PASTA_BANCO = os.path.join(BASE_DIR, "dados")
CAMINHO_BANCO = os.path.join(PASTA_BANCO, "financas.db")
PASTA_RELATORIOS = os.path.join(BASE_DIR, "relatorios")

SECRET_KEY = "chave-secreta-projeto-pucpr-financas"