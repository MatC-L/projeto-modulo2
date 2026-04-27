-- =============================================================================
-- Dashboard (camada gold)
-- =============================================================================
-- Origem: `projeto-modulo2.dataset.fact_vendas` + `dim_brick` + `dim_produto_scd2`
-- (executar depois de transform/criacao_dataset/create_and_transform_dataset.sql)
--
--   - vol_clamed_pp        <- receita onde empresa = 'Clamed'
--   - vol_concorrente_rede <- receita onde empresa = 'Concorrente'
--   - vol_concorrente_indep<- receita noutros casos (nao classificado)
--   - ean                  <- produto_id
--   - cod_prod_catarinense <- nome_produto (dim)
--   - participacao_clamed  <- % receita Clamed no total de receita do MESMO produto_id
-- =============================================================================

-- =========================================================
-- 0) Base dashboard (participacao_clamed em 0..100 por produto)
-- =========================================================
CREATE OR REPLACE TABLE `projeto-modulo2.dataset.fact_vendas_dashboard` AS
WITH linha AS (
  SELECT
    f.id_venda,
    f.fk_brick,
    f.fk_sk_produto,
    b.brick,
    f.produto_id,
    p.nome_produto AS cod_prod_catarinense,
    f.empresa,
    f.receita,
    CASE
      WHEN LOWER(TRIM(f.empresa)) = 'clamed' THEN COALESCE(f.receita, 0)
      ELSE 0
    END AS vol_clamed_pp,
    CASE
      WHEN LOWER(TRIM(f.empresa)) = 'concorrente' THEN COALESCE(f.receita, 0)
      ELSE 0
    END AS vol_concorrente_rede,
    CASE
      WHEN LOWER(TRIM(f.empresa)) IS NULL
        OR LOWER(TRIM(f.empresa)) NOT IN ('clamed', 'concorrente')
        THEN COALESCE(f.receita, 0)
      ELSE 0
    END AS vol_concorrente_indep,
    COALESCE(f.receita, 0) AS vol_total_mercado
  FROM `projeto-modulo2.dataset.fact_vendas` f
  LEFT JOIN `projeto-modulo2.dataset.dim_brick` b
    ON f.fk_brick = b.id_brick
  LEFT JOIN `projeto-modulo2.dataset.dim_produto_scd2` p
    ON f.fk_sk_produto = p.sk_produto
    AND p.flag_ativo
)
SELECT
  l.id_venda,
  l.fk_brick,
  l.fk_sk_produto,
  l.brick,
  l.produto_id AS ean,
  l.cod_prod_catarinense,
  l.vol_concorrente_indep,
  l.vol_concorrente_rede,
  l.vol_clamed_pp,
  l.vol_total_mercado,
  COALESCE(
    100 * SAFE_DIVIDE(
      SUM(l.vol_clamed_pp) OVER (PARTITION BY l.produto_id),
      NULLIF(SUM(l.vol_total_mercado) OVER (PARTITION BY l.produto_id), 0)
    ),
    0
  ) AS participacao_clamed,
  CURRENT_TIMESTAMP() AS data_carga
FROM linha l
;

-- =========================================================
-- 1) Pizza: Participação Total de Mercado
-- (categoria, volume, percentual)
-- =========================================================
CREATE OR REPLACE TABLE `projeto-modulo2.dataset.pizza_consolidado_total` AS
WITH tot AS (
  SELECT SUM(vol_total_mercado) AS total_mercado
  FROM `projeto-modulo2.dataset.fact_vendas_dashboard`
)
SELECT
  categoria,
  volume,
  (SAFE_DIVIDE(volume, tot.total_mercado) * 100) AS percentual
FROM (
  SELECT 'Clamed PP' AS categoria, SUM(vol_clamed_pp) AS volume
  FROM `projeto-modulo2.dataset.fact_vendas_dashboard`
  UNION ALL
  SELECT 'Conc. Indep.' AS categoria, SUM(vol_concorrente_indep) AS volume
  FROM `projeto-modulo2.dataset.fact_vendas_dashboard`
  UNION ALL
  SELECT 'Conc. Rede' AS categoria, SUM(vol_concorrente_rede) AS volume
  FROM `projeto-modulo2.dataset.fact_vendas_dashboard`
) x
CROSS JOIN tot
;

-- =========================================================
-- 2) Pizza: Produto com Maior Participação (agregado por produto)
-- =========================================================
CREATE OR REPLACE TABLE `projeto-modulo2.dataset.pizza_produto_destaque` AS
WITH agg AS (
  SELECT
    ean,
    ANY_VALUE(cod_prod_catarinense) AS cod_prod_catarinense,
    SUM(vol_clamed_pp) AS vol_clamed_pp,
    SUM(vol_concorrente_indep) AS vol_concorrente_indep,
    SUM(vol_concorrente_rede) AS vol_concorrente_rede,
    COALESCE(
      100 * SAFE_DIVIDE(
        SUM(vol_clamed_pp),
        NULLIF(SUM(vol_total_mercado), 0)
      ),
      0
    ) AS participacao_clamed
  FROM `projeto-modulo2.dataset.fact_vendas_dashboard`
  GROUP BY ean
)
SELECT
  ean,
  cod_prod_catarinense,
  vol_clamed_pp,
  vol_concorrente_indep,
  vol_concorrente_rede,
  participacao_clamed
FROM agg
ORDER BY participacao_clamed DESC
LIMIT 1
;

-- =========================================================
-- 3) Barras: Top 5 Produtos por Participação Clamed
-- =========================================================
CREATE OR REPLACE TABLE `projeto-modulo2.dataset.grafico_barras_top_produtos` AS
WITH agg AS (
  SELECT
    ean,
    ANY_VALUE(cod_prod_catarinense) AS cod_prod_catarinense,
    SUM(vol_clamed_pp) AS vol_clamed_pp,
    SUM(vol_concorrente_indep) AS vol_concorrente_indep,
    SUM(vol_concorrente_rede) AS vol_concorrente_rede,
    COALESCE(
      100 * SAFE_DIVIDE(
        SUM(vol_clamed_pp),
        NULLIF(SUM(vol_total_mercado), 0)
      ),
      0
    ) AS participacao_clamed
  FROM `projeto-modulo2.dataset.fact_vendas_dashboard`
  GROUP BY ean
)
SELECT
  ean,
  cod_prod_catarinense,
  vol_clamed_pp,
  vol_concorrente_indep,
  vol_concorrente_rede,
  participacao_clamed
FROM agg
ORDER BY participacao_clamed DESC
LIMIT 5
;

-- =========================================================
-- 4) Estatísticas Gerais (cards do dashboard)
-- =========================================================
CREATE OR REPLACE TABLE `projeto-modulo2.dataset.estatisticas_gerais` AS
WITH base AS (
  SELECT
    vol_total_mercado,
    vol_clamed_pp,
    vol_concorrente_indep,
    vol_concorrente_rede,
    participacao_clamed
  FROM `projeto-modulo2.dataset.fact_vendas_dashboard`
),
ordered AS (
  SELECT
    participacao_clamed,
    ROW_NUMBER() OVER (ORDER BY participacao_clamed) AS rn,
    COUNT(*) OVER () AS n
  FROM base
),
median AS (
  SELECT
    participacao_clamed AS participacao_mediana
  FROM ordered
  WHERE rn = FLOOR((n + 1) / 2)
  LIMIT 1
),
stats AS (
  SELECT
    COUNT(*) AS total_produtos,
    SUM(vol_total_mercado) AS volume_total_mercado,
    AVG(participacao_clamed) AS participacao_media,
    MAX(participacao_clamed) AS participacao_maxima,
    MIN(participacao_clamed) AS participacao_minima,
    SUM(vol_clamed_pp) AS vol_total_clamed,
    SUM(vol_concorrente_indep) + SUM(vol_concorrente_rede) AS vol_total_concorrentes
  FROM base
)
SELECT
  stats.total_produtos,
  stats.volume_total_mercado,
  stats.participacao_media,
  median.participacao_mediana,
  stats.participacao_maxima,
  stats.participacao_minima,
  stats.vol_total_clamed,
  stats.vol_total_concorrentes
FROM stats
CROSS JOIN median
;

-- =========================================================
-- TABELA TEMPORAL DE PARTICIPAÇÃO
-- =========================================================

CREATE OR REPLACE TABLE `projeto-modulo2.dataset.serie_participacao_tempo` AS
WITH base AS (
  SELECT
    DATE_TRUNC(data_venda, MONTH) AS mes_ref,
    LOWER(TRIM(empresa)) AS empresa_norm,
    COALESCE(receita, 0) AS receita
  FROM `projeto-modulo2.dataset.fact_vendas`
  WHERE data_venda IS NOT NULL
),
agg AS (
  SELECT
    mes_ref,
    SUM(CASE WHEN empresa_norm = 'clamed' THEN receita ELSE 0 END) AS receita_clamed,
    SUM(CASE WHEN empresa_norm = 'concorrente' THEN receita ELSE 0 END) AS receita_rede,
    SUM(receita) AS receita_total
  FROM base
  GROUP BY mes_ref
)
SELECT
  mes_ref,
  receita_clamed,
  receita_rede,
  SAFE_DIVIDE(receita_clamed, NULLIF(receita_total, 0)) * 100 AS share_clamed_pct,
  SAFE_DIVIDE(receita_rede, NULLIF(receita_total, 0)) * 100 AS share_rede_pct
FROM agg
ORDER BY mes_ref;