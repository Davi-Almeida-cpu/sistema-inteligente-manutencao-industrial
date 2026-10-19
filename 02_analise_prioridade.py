import sqlite3
import json
from pathlib import Path

# Localiza a pasta principal do projeto
pasta_projeto = Path(__file__).resolve().parent.parent

# Localiza o banco SQLite
caminho_banco = pasta_projeto / "projeto_manutencao.db"

# Conecta ao banco
conexao = sqlite3.connect(caminho_banco)
conexao.row_factory = sqlite3.Row

cursor = conexao.cursor()

# Consulta consolidada
consulta = """
WITH criticos AS (
    SELECT
        id_equipamento,
        COUNT(*) AS qtd_critico
    FROM leituras
    WHERE status = 'Crítico'
    GROUP BY id_equipamento
),

manutencoes_resumo AS (
    SELECT
        id_equipamento,

        SUM(
            CASE
                WHEN tipo_manutencao = 'Corretiva'
                THEN 1
                ELSE 0
            END
        ) AS qtd_corretivas,

        SUM(
            CAST(horas_parado AS REAL)
        ) AS horas_parado_total,

        SUM(
            CAST(
                REPLACE(
                    REPLACE(
                        REPLACE(custo_reais, 'R$', ''),
                        '.',
                        ''
                    ),
                    ',',
                    '.'
                )
                AS REAL
            )
        ) AS custo_total

    FROM manutencoes
    GROUP BY id_equipamento
)

SELECT
    e.id_equipamento,
    e.equipamento,
    e.criticidade,

    COALESCE(c.qtd_critico, 0) AS qtd_critico,

    COALESCE(m.qtd_corretivas, 0) AS qtd_corretivas,

    COALESCE(m.horas_parado_total, 0) AS horas_parado_total,

    COALESCE(m.custo_total, 0) AS custo_total

FROM equipamentos AS e

LEFT JOIN criticos AS c
    ON e.id_equipamento = c.id_equipamento

LEFT JOIN manutencoes_resumo AS m
    ON e.id_equipamento = m.id_equipamento
"""

cursor.execute(consulta)

equipamentos = cursor.fetchall()

resultado = []

for equipamento in equipamentos:

    score = (
        equipamento["qtd_critico"] * 3
        + equipamento["qtd_corretivas"] * 2
        + equipamento["horas_parado_total"] / 10
        + equipamento["custo_total"] / 1000
    )

    if equipamento["qtd_critico"] >= 5 and equipamento["qtd_corretivas"] >= 3:
        prioridade = "Alta"

    elif equipamento["qtd_critico"] >= 3 or equipamento["qtd_corretivas"] >= 2:
        prioridade = "Média"

    else:
        prioridade = "Baixa"

    resultado.append(
        {
            "id": equipamento["id_equipamento"],
            "equipamento": equipamento["equipamento"],
            "criticidade": equipamento["criticidade"],
            "criticos": equipamento["qtd_critico"],
            "corretivas": equipamento["qtd_corretivas"],
            "horas_paradas": equipamento["horas_parado_total"],
            "custo": equipamento["custo_total"],
            "score": score,
            "prioridade": prioridade,
        }
    )

# Ordena do maior score para o menor
resultado.sort(
    key=lambda x: x["score"],
    reverse=True
)
# Adiciona a posição do ranking
for posicao, equipamento in enumerate(resultado, start=1):
    equipamento["ranking"] = posicao

# Define onde o arquivo JSON será salvo
arquivo_json = pasta_projeto / "Python" / "ranking_prioridade.json"

# Salva o resultado em JSON
with open(arquivo_json, "w", encoding="utf-8") as arquivo:
    json.dump(
        resultado,
        arquivo,
        ensure_ascii=False,
        indent=4
    )

print("\nArquivo JSON criado com sucesso:")
print(arquivo_json)
print("\nRANKING DE PRIORIDADE DE MANUTENÇÃO\n")

for posicao, equipamento in enumerate(resultado, start=1):

    print(
        f"{posicao:02d} | "
        f"{equipamento['equipamento']} | "
        f"Score: {equipamento['score']:.2f} | "
        f"Prioridade: {equipamento['prioridade']}"
    )

conexao.close()