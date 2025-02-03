arquivo_lista_palavras = "bip39-portuguese.txt"
arquivo_texto = "texto-165.txt"
arquivo_saida = "palavras-encontradas.txt"

# Ler lista de palavras
with open(arquivo_lista_palavras, "r", encoding="utf-8") as f:
    palavras = set(f.read().splitlines())  # Usa um conjunto para melhor desempenho

# Ler texto
with open(arquivo_texto, "r", encoding="utf-8") as f:
    texto = f.read()

# Verificar quais palavras da lista estão no texto
encontradas = {palavra for palavra in palavras if palavra in texto}

# Exibir resultado
print(f"{len(encontradas)} Palavras encontradas no texto:")
print(", ".join(encontradas))

# palavras encontradas
# Salvar as palavras encontradas em um arquivo
with open(arquivo_saida, "w", encoding="utf-8") as f:
    f.write("\n".join(encontradas))