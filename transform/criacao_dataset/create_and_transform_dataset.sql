-- Bronze / staging (carga Python -> BigQuery), dataset `staging_modulo2` (US):
--   `projeto-modulo2.staging_modulo2.stg_dim_filial`
--     - filial_id (STRING)
--     - brick (STRING)
--     - regiao (STRING)
--     - cluster (STRING)
--
--   `projeto-modulo2.staging_modulo2.stg_dim_produto`
--     - produto_id (STRING)
--     - categoria (STRING)
--     - nome_produto (STRING)
--
--   `projeto-modulo2.staging_modulo2.stg_fato_vendas`
--     - data (DATE / STRING / TIMESTAMP conforme inferencia na carga)
--     - produto_id, filial_id, empresa (STRING)
--     - volume, preco_unitario, receita (NUMERIC/FLOAT64)
--
-- Ordem de execucao: dim_brick -> dim_filial -> dim_produto_scd2 -> fact_vendas
--   (dim_produto antes do fato para fk_sk_produto -> sk_produto)
--
-- Silver: tabelas geradas no dataset `dataset` (leitura do staging acima):
--   dim_brick, dim_filial, dim_produto_scd2, fact_vendas
-- =============================================================================

-- =========================================================
-- 1) DIM_BRICK
-- =========================================================
CREATE OR REPLACE TABLE `projeto-modulo2.dataset.dim_brick` AS
SELECT
  ROW_NUMBER() OVER (ORDER BY brick) AS id_brick,
  brick,
  CURRENT_TIMESTAMP() AS data_cadastro
FROM (
  SELECT DISTINCT TRIM(CAST(brick AS STRING)) AS brick
  FROM `projeto-modulo2.staging_modulo2.stg_dim_filial`
  WHERE brick IS NOT NULL
    AND TRIM(CAST(brick AS STRING)) != ''
);

-- =========================================================
-- 2) DIM_FILIAL
--    Uma linha por loja (filial_id), com FK para territorio brick.
-- =========================================================
CREATE OR REPLACE TABLE `projeto-modulo2.dataset.dim_filial` AS
WITH filial_base AS (
  SELECT
    TRIM(CAST(filial_id AS STRING)) AS filial_id,
    TRIM(CAST(brick AS STRING)) AS brick,
    TRIM(CAST(regiao AS STRING)) AS regiao,
    TRIM(CAST(cluster AS STRING)) AS cluster
  FROM `projeto-modulo2.staging_modulo2.stg_dim_filial`
  WHERE filial_id IS NOT NULL
    AND brick IS NOT NULL
),
filial_dedup AS (
  SELECT
    filial_id,
    ANY_VALUE(brick) AS brick,
    ANY_VALUE(regiao) AS regiao,
    ANY_VALUE(cluster) AS cluster
  FROM filial_base
  GROUP BY filial_id
),
filial_com_fk AS (
  SELECT
    d.filial_id,
    d.regiao,
    d.cluster,
    b.id_brick AS fk_brick
  FROM filial_dedup d
  JOIN `projeto-modulo2.dataset.dim_brick` b
    ON d.brick = b.brick
)
SELECT
  ROW_NUMBER() OVER (ORDER BY fk_brick, filial_id) AS id_filial,
  filial_id,
  regiao,
  cluster,
  fk_brick,
  CURRENT_TIMESTAMP() AS data_cadastro
FROM filial_com_fk;

-- =========================================================
-- 3) DIM_PRODUTO_SCD2
--    surrogate sk + chave natural + metrica agregada.
--    Aqui id_produto_original = produto_id; valor_produto = soma de receita na fato (staging).
-- =========================================================
CREATE OR REPLACE TABLE `projeto-modulo2.dataset.dim_produto_scd2` (
  sk_produto INT64,
  id_produto_original STRING,
  categoria STRING,
  nome_produto STRING,
  valor_produto NUMERIC,
  data_inicio_validade TIMESTAMP,
  data_fim_validade TIMESTAMP,
  flag_ativo BOOL
)
AS
WITH receita_por_produto AS (
  SELECT
    TRIM(CAST(produto_id AS STRING)) AS produto_id,
    SUM(COALESCE(SAFE_CAST(receita AS NUMERIC), 0)) AS receita_total
  FROM `projeto-modulo2.staging_modulo2.stg_fato_vendas`
  WHERE TRIM(CAST(produto_id AS STRING)) IS NOT NULL
    AND TRIM(CAST(produto_id AS STRING)) != ''
  GROUP BY produto_id
),
produto_dim AS (
  SELECT
    TRIM(CAST(produto_id AS STRING)) AS id_produto_original,
    TRIM(CAST(categoria AS STRING)) AS categoria,
    TRIM(CAST(nome_produto AS STRING)) AS nome_produto
  FROM `projeto-modulo2.staging_modulo2.stg_dim_produto`
  WHERE TRIM(CAST(produto_id AS STRING)) IS NOT NULL
)
SELECT
  ROW_NUMBER() OVER (ORDER BY p.id_produto_original) AS sk_produto,
  p.id_produto_original,
  p.categoria,
  p.nome_produto,
  COALESCE(r.receita_total, 0) AS valor_produto,
  CURRENT_TIMESTAMP() AS data_inicio_validade,
  CAST(NULL AS TIMESTAMP) AS data_fim_validade,
  TRUE AS flag_ativo
FROM produto_dim p
LEFT JOIN receita_por_produto r
  ON p.id_produto_original = r.produto_id;

-- =========================================================
-- 4) FACT_VENDAS
--    Grao: linha de venda no staging; FKs para dim_filial e dim_produto_scd2 (versao ativa).
-- =========================================================
CREATE OR REPLACE TABLE `projeto-modulo2.dataset.fact_vendas` AS
WITH vendas_base AS (
  SELECT
    COALESCE(
      SAFE_CAST(data AS DATE),
      SAFE.PARSE_DATE('%Y-%m-%d', SUBSTR(TRIM(CAST(data AS STRING)), 1, 10))
    ) AS data_venda,
    TRIM(CAST(produto_id AS STRING)) AS produto_id,
    TRIM(CAST(filial_id AS STRING)) AS filial_id,
    TRIM(CAST(empresa AS STRING)) AS empresa,
    COALESCE(SAFE_CAST(volume AS NUMERIC), 0) AS volume,
    COALESCE(SAFE_CAST(preco_unitario AS NUMERIC), 0) AS preco_unitario,
    COALESCE(SAFE_CAST(receita AS NUMERIC), 0) AS receita
  FROM `projeto-modulo2.staging_modulo2.stg_fato_vendas`
  WHERE produto_id IS NOT NULL
    AND filial_id IS NOT NULL
)
SELECT
  ROW_NUMBER() OVER (ORDER BY v.data_venda, v.filial_id, v.produto_id) AS id_venda,
  f.id_filial AS fk_id_filial,
  f.fk_brick,
  p.sk_produto AS fk_sk_produto,
  v.data_venda,
  v.produto_id,
  v.filial_id,
  v.empresa,
  v.volume,
  v.preco_unitario,
  v.receita,
  COALESCE(v.volume * v.preco_unitario, 0) AS volume_x_preco,
  CURRENT_TIMESTAMP() AS data_carga
FROM vendas_base v
JOIN `projeto-modulo2.dataset.dim_filial` f
  ON v.filial_id = f.filial_id
LEFT JOIN `projeto-modulo2.dataset.dim_produto_scd2` p
  ON v.produto_id = p.id_produto_original
  AND p.flag_ativo;
