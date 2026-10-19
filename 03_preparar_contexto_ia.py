import json
from pathlib import Path

# Localiza a pasta principal do projeto
pasta_projeto = Path(__file__).resolve().parent.parent

# Arquivos utilizados
arquivo_json = pasta_projeto / "Python" / "ranking_prioridade.json"
arquivo_contexto = pasta_projeto / "Python" / "contexto_ia.txt"

# Lê o ranking criado pelo script anterior
with open(arquivo_json, "r", encoding="utf-8") as arquivo:
    ranking = json.load(arquivo)

# Seleciona somente os 5 equipamentos mais prioritários
top_5 = ranking[:5]

contexto = """
Você é um assistente especializado em análise de manutenção industrial.

Analise exclusivamente os dados fornecidos abaixo.

REGRAS IMPORTANTES:

1. Não invente datas. O período analisado é de 01/01/2026 a 25/01/2026.

2. Não invente falhas, componentes defeituosos ou causas técnicas.

3. Quando sugerir uma possível causa, identifique explicitamente como:
   "Hipótese a investigar".

4. Diferencie sempre:
   - Fato observado nos dados
   - Hipótese técnica
   - Recomendação

5. O Score de Prioridade foi calculado pela seguinte regra:

   Score =
   (Eventos Críticos × 3)
   + (Manutenções Corretivas × 2)
   + (Horas Paradas ÷ 10)
   + (Custo Total ÷ 1000)

6. A criticidade do equipamento NÃO faz parte matematicamente do Score.
   Ela deve ser utilizada apenas como informação adicional para interpretação.

7. Não apresente como certeza nenhuma informação que não esteja nos dados.

Produza:

1. Resumo executivo
2. Equipamentos que exigem maior atenção
3. Fatos observados nos dados
4. Hipóteses que merecem investigação
5. Recomendações de inspeção e manutenção

DADOS DOS EQUIPAMENTOS:
"""

for equipamento in top_5:

    contexto += f"""
Ranking: {equipamento['ranking']}
Equipamento: {equipamento['equipamento']}
ID: {equipamento['id']}
Criticidade: {equipamento['criticidade']}
Eventos críticos: {equipamento['criticos']}
Manutenções corretivas: {equipamento['corretivas']}
Horas paradas: {equipamento['horas_paradas']}
Custo total: R$ {equipamento['custo']:.2f}
Score de prioridade: {equipamento['score']:.2f}
Prioridade: {equipamento['prioridade']}
------------------------------
"""

# Salva o contexto
with open(arquivo_contexto, "w", encoding="utf-8") as arquivo:
    arquivo.write(contexto)

print("Contexto para IA criado com sucesso!")
print(arquivo_contexto)