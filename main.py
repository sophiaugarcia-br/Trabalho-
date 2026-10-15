from flask import Flask
 
    saidas = []

    print("=== CONTROLE DE FINANÇAS ESTUDANTIS ===")

    print("\nENTRADAS")
    while True:
        try:
            entrada = float(input("Digite as entradas de capital desse mês (0 para sair): "))
            if entrada == 0:
                break
            if entrada < 0:
                print("Digite um valor positivo.")
                continue
            descricao = input("Categoria da entrada")
            entradas.append({"descricao": descricao, "valor": entrada})
        except ValueError:
            print("Entrada inválida. Por favor, digite um valor válido.")

    print("\nSAÍDAS")
    print("Categorias: Alimentação, Transporte, Moradia, Lazer")

    while True:
        try:
            saida = float(input("Digite as saídas de capital desse mês (0 para sair): "))
            if saida == 0:
                break
            if saida < 0:
                print("Digite um valor positivo.")
                continue

            categoria = input("Categoria de despesa").strip().capitalize()
            if not categoria:
                categoria = "Outros"
            saidas.append({"categoria": categoria, "valor": saida})
        except ValueError:
            print("Entrada inválida. Por favor, digite um valor válido.")

    return entradas, saidas

def relatorio(entradas, saidas):
    total_entradas = sum(item["valor"] for item in entradas)
    total_saidas = sum(item["valor"] for item in saidas)
    sobra = total_entradas - total_saidas

    print("\n")
    print("RELATÓRIO MENSAL")
    print(f"Total de entradas: R${total_entradas:.2f}")
    print(f"Total de saídas: R${total_saidas:.2f}")
    print(f"Saldo final: R${sobra:.2f}")

    if saidas:
        print("\nGastos por Categoria:")
        gastos_por_categoria = {}
        for item in saidas:
            cat = item["categoria"]
            val = item["valor"]
            gastos_por_categoria[cat] = gastos_por_categoria.get(cat, 0.0) + val

        for cat, val in gastos_por_categoria.items():
            print(f"  • {cat}: R$ {val:.2f}")
    print("=" * 35)

if __name__ == "__main__":
    e, s = registrar_transacoes
    relatorio(e, s)