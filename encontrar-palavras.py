import re

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
# Criar um conjunto com todas as palavras do texto (separadas corretamente)
texto_formatado = texto.lower().replace(',', '').replace('.', '')
palavras_texto = set(re.findall(r'\b\w+\b', texto_formatado))

# Encontrar palavras da lista que estão exatamente no texto
encontradas = palavras.intersection(palavras_texto)

# Exibir resultado
print(f"{len(encontradas)} Palavras encontradas no texto:")
print(", ".join(encontradas))

# palavras encontradas
# Salvar as palavras encontradas em um arquivo
with open(arquivo_saida, "w", encoding="utf-8") as f:
    f.write("\n".join(encontradas))