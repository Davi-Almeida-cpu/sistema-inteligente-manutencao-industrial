import json
import urllib.request
from pathlib import Path

# Pasta principal do projeto
pasta_projeto = Path(__file__).resolve().parent.parent

# Arquivos
arquivo_contexto = pasta_projeto / "Python" / "contexto_ia.txt"
arquivo_saida = pasta_projeto / "Python" / "insights_ia.json"

# Lê o contexto preparado anteriormente
with open(arquivo_contexto, "r", encoding="utf-8") as arquivo:
    contexto = arquivo.read()

# Define exatamente o formato que queremos receber da IA
schema = {
    "type": "object",
    "properties": {
        "periodo_analisado": {
            "type": "string"
        },
        "equipamento_prioritario": {
            "type": "string"
        },
        "prioridade": {
            "type": "string"
        },
        "resumo_executivo": {
            "type": "string"
        },
        "fatos_observados": {
            "type": "array",
            "items": {"type": "string"}
        },
        "hipoteses_investigar": {
            "type": "array",
            "items": {"type": "string"}
        },
        "recomendacoes": {
            "type": "array",
            "items": {"type": "string"}
        },
        "dados_adicionais_recomendados": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": [
        "periodo_analisado",
        "equipamento_prioritario",
        "prioridade",
        "resumo_executivo",
        "fatos_observados",
        "hipoteses_investigar",
        "recomendacoes",
        "dados_adicionais_recomendados"
    ]
}

prompt = f"""
Analise os dados fornecidos abaixo.

REGRAS:

- Use somente os números e fatos presentes nos dados.
- Não invente datas.
- Não transforme hipóteses em fatos.
- Não declare que um equipamento está em condição satisfatória apenas por ter
  score menor que os demais.
- Se sugerir uma causa técnica não comprovada, coloque-a somente em
  hipoteses_investigar.
- Se recomendar coletar uma variável que não existe nos dados atuais,
  coloque-a somente em dados_adicionais_recomendados.
- Retorne exclusivamente os campos definidos no formato solicitado.

DADOS:

{contexto}
"""

dados = {
    "model": "gemma3:4b",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "stream": False,
    "format": schema,
    "options": {
        "temperature": 0
    }
}

dados_json = json.dumps(dados).encode("utf-8")

requisicao = urllib.request.Request(
    "http://localhost:11434/api/chat",
    data=dados_json,
    headers={"Content-Type": "application/json"},
    method="POST"
)

print("Gerando insights estruturados...")

try:
    with urllib.request.urlopen(requisicao) as resposta:
        resultado = json.loads(
            resposta.read().decode("utf-8")
        )

    # O conteúdo devolvido pelo modelo já deve ser um JSON
    conteudo = resultado["message"]["content"]

    insights = json.loads(conteudo)

    with open(arquivo_saida, "w", encoding="utf-8") as arquivo:
        json.dump(
            insights,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    print("\nInsights estruturados criados com sucesso!")
    print(arquivo_saida)

except Exception as erro:
    print("\nOcorreu um erro:")
    print(erro)