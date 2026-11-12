import os
import config

def executar():
    # Garante que as pastas dados/ e relatorios/ existam
    os.makedirs(os.path.dirname(config.CAMINHO_BANCO), exist_ok=True)
    os.makedirs(config.PASTA_RELATORIOS, exist_ok=True)
    print("Inicialização básica concluída!")