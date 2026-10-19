-- ============================================================
-- PROJETO: SISTEMA DE ANÁLISE DE MANUTENÇÃO INDUSTRIAL
-- ETAPA: ANÁLISE SQL
-- BANCO: projeto_manutencao.db
--
-- TABELAS:
-- equipamentos  -> 20 equipamentos cadastrados
-- leituras      -> 500 registros operacionais
-- manutencoes   -> 60 ordens de serviço
-- ============================================================



-- ============================================================
-- 01. VALIDAÇÃO DAS TABELAS
-- Objetivo: confirmar se todos os dados foram importados.
-- ============================================================

-- Quantidade de equipamentos
SELECT
    COUNT(*) AS total_equipamentos
FROM equipamentos;


-- Quantidade de leituras
SELECT
    COUNT(*) AS total_leituras
FROM leituras;


-- Quantidade de ordens de serviço
SELECT
    COUNT(*) AS total_manutencoes
FROM manutencoes;



-- ============================================================
-- 02. VISUALIZAÇÃO INICIAL DOS DADOS
-- Objetivo: visualizar amostras das tabelas.
-- ============================================================

-- Todos os equipamentos
SELECT *
FROM equipamentos;


-- Primeiras 10 leituras
SELECT *
FROM leituras
LIMIT 10;


-- Algumas colunas específicas das leituras
SELECT
    id_leitura,
    id_equipamento,
    temperatura_c,
    vibracao_mm_s,
    status
FROM leituras
LIMIT 10;


-- Primeiras 10 ordens de manutenção
SELECT *
FROM manutencoes
LIMIT 10;



-- ============================================================
-- 03. ANÁLISE DOS STATUS DAS LEITURAS
-- Objetivo: entender a distribuição das condições operacionais.
-- ============================================================

-- Mostrar somente leituras críticas
SELECT *
FROM leituras
WHERE status = 'Crítico';


-- Quantidade total de leituras críticas
SELECT
    COUNT(*) AS total_criticos
FROM leituras
WHERE status = 'Crítico';


-- Quantidade de registros por status
SELECT
    status,
    COUNT(*) AS quantidade
FROM leituras
GROUP BY status
ORDER BY quantidade DESC;



-- ============================================================
-- 04. EVENTOS CRÍTICOS POR EQUIPAMENTO
-- Objetivo: identificar quais equipamentos apresentaram
-- maior frequência de condições críticas.
-- ============================================================

SELECT
    id_equipamento,
    COUNT(*) AS qtd_critico
FROM leituras
WHERE status = 'Crítico'
GROUP BY id_equipamento
ORDER BY qtd_critico DESC;



-- ============================================================
-- 05. ANÁLISE DAS MANUTENÇÕES
-- Objetivo: entender quantidade, downtime e custos.
-- ============================================================

-- Quantidade de manutenções por tipo
SELECT
    tipo_manutencao,
    COUNT(*) AS quantidade
FROM manutencoes
GROUP BY tipo_manutencao;


-- Total de horas de equipamento parado
SELECT
    SUM(horas_parado) AS total_horas_parado
FROM manutencoes;


-- Custo total de manutenção
SELECT
    SUM(custo_reais) AS custo_total
FROM manutencoes;


-- Indicadores de manutenção por equipamento
SELECT
    id_equipamento,

    COUNT(
        CASE
            WHEN tipo_manutencao = 'Corretiva'
            THEN 1
        END
    ) AS qtd_corretivas,

    SUM(horas_parado) AS horas_parado_total,

    ROUND(
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
    ),
    2
) AS custo_total

FROM manutencoes

GROUP BY id_equipamento

ORDER BY custo_total DESC;



-- ============================================================
-- 06. PRIMEIRO JOIN
-- Objetivo: combinar informações das tabelas
-- manutencoes e equipamentos.
-- ============================================================

SELECT
    m.id_os,
    m.id_equipamento,
    e.equipamento,
    e.tipo,
    m.tipo_manutencao,
    m.falha

FROM manutencoes AS m

INNER JOIN equipamentos AS e
    ON m.id_equipamento = e.id_equipamento

LIMIT 10;



-- ============================================================
-- 07. CORRETIVAS POR EQUIPAMENTO + NOME DO EQUIPAMENTO
-- Objetivo: descobrir quais máquinas concentraram
-- mais intervenções corretivas.
-- ============================================================

SELECT
    m.id_equipamento,
    e.equipamento,
    COUNT(*) AS qtd_corretivas

FROM manutencoes AS m

INNER JOIN equipamentos AS e
    ON m.id_equipamento = e.id_equipamento

WHERE m.tipo_manutencao = 'Corretiva'

GROUP BY
    m.id_equipamento,
    e.equipamento

ORDER BY qtd_corretivas DESC;



-- ============================================================
-- 08. ANÁLISE CONSOLIDADA POR EQUIPAMENTO
--
-- Objetivo:
-- Unir indicadores de sensores e manutenção.
--
-- Indicadores:
-- - quantidade de eventos críticos
-- - temperatura média
-- - vibração média
-- - quantidade de corretivas
-- - horas totais de parada
-- - custo total
-- ============================================================

WITH criticos AS (

    SELECT
        id_equipamento,
        COUNT(*) AS qtd_critico

    FROM leituras

    WHERE status = 'Crítico'

    GROUP BY id_equipamento
),


medias AS (

    SELECT
        id_equipamento,

        ROUND(
            AVG(CAST(temperatura_c AS REAL)),
            1
        ) AS temp_media_c,

        ROUND(
            AVG(
                CAST(
                    REPLACE(vibracao_mm_s, ',', '.')
                    AS REAL
                )
            ),
            1
        ) AS vibracao_media_mm_s

    FROM leituras

    GROUP BY id_equipamento
),


manut AS (

    SELECT
        id_equipamento,

        COUNT(
            CASE
                WHEN tipo_manutencao = 'Corretiva'
                THEN 1
            END
        ) AS qtd_corretivas,

        SUM(horas_parado) AS horas_parado_total,

        ROUND(
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
    ),
    2
) AS custo_total

    FROM manutencoes

    GROUP BY id_equipamento
)


SELECT
    e.id_equipamento,
    e.equipamento,
    e.tipo,
    e.criticidade,

    COALESCE(c.qtd_critico, 0)
        AS qtd_critico,

    md.temp_media_c,

    md.vibracao_media_mm_s,

    COALESCE(m.qtd_corretivas, 0)
        AS qtd_corretivas,

    COALESCE(m.horas_parado_total, 0)
        AS horas_parado_total,

    COALESCE(m.custo_total, 0)
        AS custo_total
FROM equipamentos AS e

LEFT JOIN criticos AS c
    ON e.id_equipamento = c.id_equipamento

LEFT JOIN medias AS md
    ON e.id_equipamento = md.id_equipamento

LEFT JOIN manut AS m
    ON e.id_equipamento = m.id_equipamento

ORDER BY
    CASE
        WHEN COALESCE(c.qtd_critico, 0) >= 5
             AND COALESCE(m.qtd_corretivas, 0) >= 3
        THEN 1

        WHEN COALESCE(c.qtd_critico, 0) >= 3
             OR COALESCE(m.qtd_corretivas, 0) >= 2
        THEN 2

        ELSE 3
    END,

    COALESCE(c.qtd_critico, 0) DESC,
    COALESCE(m.custo_total, 0) DESC;