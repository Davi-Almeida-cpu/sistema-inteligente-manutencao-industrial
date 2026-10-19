import json
import urllib.request
from pathlib import Path

# Localiza a pasta principal do projeto
pasta_projeto = Path(__file__).resolve().parent.parent

# Arquivo preparado pelo script anterior
arquivo_contexto = pasta_projeto / "Python" / "contexto_ia.txt"

# Arquivo onde a resposta da IA será salva
arquivo_saida = pasta_projeto / "Python" / "analise_ia.txt"

# Lê o contexto
with open(arquivo_contexto, "r", encoding="utf-8") as arquivo:
    contexto = arquivo.read()

# Dados enviados ao Ollama
dados = {
    "model": "gemma3:4b",
    "prompt": contexto,
    "stream": False
}

dados_json = json.dumps(dados).encode("utf-8")

# Endereço local do Ollama
url = "http://localhost:11434/api/generate"

requisicao = urllib.request.Request(
    url,
    data=dados_json,
    headers={"Content-Type": "application/json"},
    method="POST"
)

print("Enviando dados para a IA local...")

try:
    with urllib.request.urlopen(requisicao) as resposta:
        resultado = json.loads(resposta.read().decode("utf-8"))

    analise = resultado["response"]

    with open(arquivo_saida, "w", encoding="utf-8") as arquivo:
        arquivo.write(analise)

    print("\nAnálise concluída com sucesso!")
    print("Arquivo criado:")
    print(arquivo_saida)

except Exception as erro:
    print("\nOcorreu um erro:")
    print(erro)